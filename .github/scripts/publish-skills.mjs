#!/usr/bin/env node
/**
 * Publish a skills repository to its Cloud Storage bucket.
 *
 * THIS FILE IS VENDORED. The canonical copy lives in content-generator at
 * `ci/publish-skills.mjs`; `.github/scripts/publish-skills.mjs` in each skills
 * repository is a byte-for-byte copy of it. `npm run ci:check-vendored` in the
 * engine fails if they have drifted. Edit the canonical copy and re-vendor;
 * never patch one repository's copy alone.
 *
 * It is vendored rather than imported so a skills repository can publish
 * itself with nothing but a checkout and a short-lived federated token -- no
 * access to the private engine, no credential beyond the one that writes to
 * its own bucket.
 *
 * The "upload only what changed" check compares the md5 of the zip this run
 * built against the md5 in the bucket. That is only stable while the
 * compressor is: deflate output differs between zlib versions, so the same
 * files built on a different Node produce a different archive and every
 * package looks changed. The workflow pins `node-version: "22"`, which floats
 * across patch releases, so expect an occasional run that re-uploads
 * everything after a runner bump. Content stays correct -- it is the skip
 * optimisation that lapses, not the result. Comparing a hash of the package's
 * *inputs* held in object metadata would be immune to this; it is not worth
 * the complexity until the archives get big.
 *
 * The repository is the source of truth. Every run rebuilds `index.json` from
 * what is on disk, so deleting a package directory removes it from the
 * catalogue; there is no accumulated state to reconcile.
 *
 * Reads `skills.config.json` at the repository root:
 *   { "bucket": "...", "prefix": "skills/", "publicBaseUrl": "https://..." }
 *
 * Environment:
 *   GCS_ACCESS_TOKEN     OAuth access token with write access to the bucket.
 *   SKILLS_BUNDLE_KEY    Full object key for the everything-bundle. REQUIRED
 *                        and never generated here: the unguessable filename is
 *                        the only thing gating the bundle, other repositories
 *                        hold the same value, and minting a fresh one on every
 *                        push would silently rotate the secret and break them.
 *   DRY_RUN              Any non-empty value lists the work and uploads nothing.
 */
import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import zlib from "node:zlib";

/* ------------------------------------------------------------------ *
 * zip -- copied verbatim from content-generator lib/publish/zip.mjs.
 * Entries carry a zero mod-time, so identical content yields identical
 * bytes and an unchanged skill can be detected and skipped.
 * ------------------------------------------------------------------ */

function u16(n) {
  const b = Buffer.alloc(2);
  b.writeUInt16LE(n & 0xffff);
  return b;
}

function u32(n) {
  const b = Buffer.alloc(4);
  b.writeUInt32LE(n >>> 0);
  return b;
}

/** @param {{ name: string, data: Buffer | string }[]} entries */
export function zipBuffers(entries) {
  const list = Array.isArray(entries) ? entries : [];
  const locals = [];
  const centrals = [];
  let offset = 0;
  for (const entry of list) {
    const name = String(entry.name || "").replaceAll("\\", "/").replace(/^\/+/u, "");
    if (!name) throw new Error("zip entry is missing a name");
    const nameBuf = Buffer.from(name, "utf8");
    const data = Buffer.isBuffer(entry.data) ? entry.data : Buffer.from(String(entry.data ?? ""), "utf8");
    const crc = zlib.crc32(data);
    const compressed = zlib.deflateRawSync(data);
    const local = Buffer.concat([
      Buffer.from([0x50, 0x4b, 0x03, 0x04]),
      u16(20), u16(0), u16(8), u16(0), u16(0),
      u32(crc), u32(compressed.length), u32(data.length),
      u16(nameBuf.length), u16(0),
      nameBuf, compressed,
    ]);
    const central = Buffer.concat([
      Buffer.from([0x50, 0x4b, 0x01, 0x02]),
      u16(20), u16(20), u16(0), u16(8), u16(0), u16(0),
      u32(crc), u32(compressed.length), u32(data.length),
      u16(nameBuf.length), u16(0), u16(0), u16(0), u16(0),
      u32(0), u32(offset),
      nameBuf,
    ]);
    locals.push(local);
    centrals.push(central);
    offset += local.length;
  }
  const centralBuf = Buffer.concat(centrals);
  const end = Buffer.concat([
    Buffer.from([0x50, 0x4b, 0x05, 0x06]),
    u16(0), u16(0), u16(list.length), u16(list.length),
    u32(centralBuf.length), u32(offset), u16(0),
  ]);
  return Buffer.concat([...locals, centralBuf, end]);
}

/** @param {string} skillName @param {{ path: string, data: Buffer }[]} files */
export function zipSkillPackage(skillName, files) {
  const name = String(skillName || "").trim();
  if (!name) throw new Error("zipSkillPackage requires a skill name");
  const seen = new Set();
  const entries = [];
  for (const f of files) {
    const rel = String(f.path || "").replaceAll("\\", "/").replace(/^\/+/u, "");
    if (!rel) throw new Error("skill package file is missing a path");
    if (rel.split("/").includes("..")) throw new Error(`skill package path escapes the package: ${f.path}`);
    if (seen.has(rel)) throw new Error(`duplicate skill package path: ${rel}`);
    seen.add(rel);
    entries.push({ name: `${name}/${rel}`, data: f.data });
  }
  if (!seen.has("SKILL.md")) throw new Error(`skill package for "${name}" has no SKILL.md`);
  entries.sort((a, b) => (a.name < b.name ? -1 : a.name > b.name ? 1 : 0));
  return zipBuffers(entries);
}

/* ------------------------------------------------------------------ *
 * package discovery -- mirrors lib/content-types/skill-package.mjs
 * ------------------------------------------------------------------ */

export const EXCLUDED_DIRS = new Set([
  ".git", ".claude", ".venv", "venv", "node_modules", "__pycache__",
  ".pytest_cache", ".mypy_cache", ".ruff_cache", ".idea", ".vscode",
  "output", "dist", "build", ".egg-info",
]);
export const EXCLUDED_FILES = new Set([".DS_Store", "Thumbs.db", ".env", "SKILL.json"]);
const MAX_PACKAGE_FILES = 500;
const MAX_PACKAGE_BYTES = 25 * 1024 * 1024;

const HTML_CACHE_CONTROL = "public, max-age=300";
const ASSET_CACHE_CONTROL = "public, max-age=31536000, immutable";

/** @param {string} root @param {string} prefix */
export async function listPackageFiles(root, prefix = "") {
  const dir = prefix ? path.join(root, prefix) : root;
  let entries = [];
  try {
    entries = await fs.readdir(dir, { withFileTypes: true });
  } catch {
    return [];
  }
  const out = [];
  for (const e of entries) {
    const rel = prefix ? `${prefix}/${e.name}` : e.name;
    if (e.isDirectory()) {
      if (EXCLUDED_DIRS.has(e.name) || e.name.endsWith(".egg-info")) continue;
      out.push(...(await listPackageFiles(root, rel)));
      continue;
    }
    if (!e.isFile() || EXCLUDED_FILES.has(e.name)) continue;
    out.push(rel);
  }
  return out.sort();
}

/**
 * The frontmatter fields the catalogue needs.
 *
 * Deliberately not the engine's full validator: that lives with the engine and
 * stays the strict gate (`npm run skills:check`). CI checks only what it must
 * to publish a coherent catalogue, so the rules cannot quietly fork.
 * @param {string} text
 */
export function frontmatter(text) {
  const m = /^---\r?\n([\s\S]*?)\r?\n---/u.exec(String(text || ""));
  if (!m) return {};
  const out = {};
  const lines = m[1].split(/\r?\n/u);
  for (let i = 0; i < lines.length; i++) {
    const kv = /^([A-Za-z0-9_-]+):\s*(.*)$/u.exec(lines[i]);
    if (!kv) continue;
    const value = kv[2].trim();
    // A block scalar (`>`, `>-`, `|`, `|-`) or a bare `key:` puts the value on
    // the indented lines below. A third of the skills write their description
    // that way, and reading only the first line gave the catalogue an empty
    // string -- or, worse, a literal ">" -- for every one of them.
    //
    // Fold the continuation, as the engine's parser does in
    // lib/content-types/skill-spec.mjs. That parser also turns an indented
    // `key: value` run into a nested map, for `metadata:`. This one does not:
    // it reads name, description and version, which are all scalars.
    if (value === "" || value === ">" || value === ">-" || value === "|" || value === "|-") {
      const block = [];
      while (i + 1 < lines.length && /^\s+\S/u.test(lines[i + 1])) block.push(lines[++i].trim());
      out[kv[1]] = block.join(" ").trim();
      continue;
    }
    out[kv[1]] = value.replace(/^["']|["']$/gu, "");
  }
  return out;
}

/**
 * Every package in the repository, as `<platform>/<name>/SKILL.md`.
 * @param {string} root
 */
export async function findPackages(root) {
  const packages = [];
  const problems = [];
  for (const platform of (await fs.readdir(root, { withFileTypes: true })).sort((a, b) => a.name.localeCompare(b.name))) {
    if (!platform.isDirectory() || platform.name.startsWith(".") || EXCLUDED_DIRS.has(platform.name)) continue;
    const platformDir = path.join(root, platform.name);
    for (const pkg of (await fs.readdir(platformDir, { withFileTypes: true })).sort((a, b) => a.name.localeCompare(b.name))) {
      if (!pkg.isDirectory()) continue;
      const dir = path.join(platformDir, pkg.name);
      let text;
      try {
        text = await fs.readFile(path.join(dir, "SKILL.md"), "utf8");
      } catch {
        continue; // a directory without SKILL.md is not a package
      }
      const fm = frontmatter(text);
      if (fm.name && fm.name !== pkg.name) {
        problems.push(`${platform.name}/${pkg.name}: SKILL.md declares name "${fm.name}", which must match the directory.`);
        continue;
      }
      const rels = await listPackageFiles(dir);
      if (rels.length > MAX_PACKAGE_FILES) {
        problems.push(`${platform.name}/${pkg.name}: ${rels.length} files, over the ${MAX_PACKAGE_FILES} limit.`);
        continue;
      }
      const files = [];
      for (const rel of rels) files.push({ path: rel, data: await fs.readFile(path.join(dir, rel)) });
      const bytes = files.reduce((n, f) => n + f.data.length, 0);
      if (bytes > MAX_PACKAGE_BYTES) {
        problems.push(`${platform.name}/${pkg.name}: ${(bytes / 1048576).toFixed(1)}MB, over the 25MB limit.`);
        continue;
      }
      packages.push({
        platform: platform.name,
        name: pkg.name,
        description: String(fm.description || ""),
        version: Number(fm.version) > 0 ? Number(fm.version) : 1,
        files,
      });
    }
  }
  return { packages, problems };
}

/* ------------------------------------------------------------------ *
 * Cloud Storage over the JSON API. A bearer token is all it needs, so
 * CI carries no SDK.
 * ------------------------------------------------------------------ */

const GCS = "https://storage.googleapis.com/storage/v1/b";
const GCS_UPLOAD = "https://storage.googleapis.com/upload/storage/v1/b";

/** @param {{ bucket: string, prefix: string, token: string }} o */
async function listObjects(o) {
  const out = new Map();
  let pageToken = "";
  do {
    const q = new URLSearchParams({ maxResults: "1000", prefix: o.prefix });
    if (pageToken) q.set("pageToken", pageToken);
    const res = await fetch(`${GCS}/${encodeURIComponent(o.bucket)}/o?${q}`, {
      headers: { Authorization: `Bearer ${o.token}` },
    });
    if (!res.ok) throw new Error(`Listing gs://${o.bucket} returned ${res.status}: ${await res.text()}`);
    const body = await res.json();
    for (const item of body.items || []) out.set(String(item.name), String(item.md5Hash || ""));
    pageToken = String(body.nextPageToken || "");
  } while (pageToken);
  return out;
}

/** @param {{ bucket: string, object: string, body: Buffer, contentType: string, cacheControl: string, token: string }} o */
async function upload(o) {
  const boundary = `b${crypto.randomBytes(16).toString("hex")}`;
  const meta = JSON.stringify({ name: o.object, contentType: o.contentType, cacheControl: o.cacheControl });
  const payload = Buffer.concat([
    Buffer.from(`--${boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n${meta}\r\n--${boundary}\r\nContent-Type: ${o.contentType}\r\n\r\n`, "utf8"),
    o.body,
    Buffer.from(`\r\n--${boundary}--\r\n`, "utf8"),
  ]);
  const res = await fetch(`${GCS_UPLOAD}/${encodeURIComponent(o.bucket)}/o?uploadType=multipart`, {
    method: "POST",
    headers: { Authorization: `Bearer ${o.token}`, "Content-Type": `multipart/related; boundary=${boundary}` },
    body: payload,
  });
  if (!res.ok) throw new Error(`Uploading ${o.object} returned ${res.status}: ${await res.text()}`);
}

/** GCS reports md5 base64-encoded. @param {Buffer} buf */
function md5(buf) {
  return crypto.createHash("md5").update(buf).digest("base64");
}

/* ------------------------------------------------------------------ */

export async function main() {
  const root = process.cwd();
  const dryRun = Boolean(process.env.DRY_RUN);
  const cfg = JSON.parse(await fs.readFile(path.join(root, "skills.config.json"), "utf8"));
  const bucket = String(cfg.bucket || "").trim();
  if (!bucket) throw new Error("skills.config.json needs a bucket.");
  const prefix = String(cfg.prefix || "skills/").replace(/^\/+/u, "").replace(/\/?$/u, "/");
  const publicBaseUrl = String(cfg.publicBaseUrl || `https://storage.googleapis.com/${bucket}`).replace(/\/+$/u, "");
  const bundleKey = String(process.env.SKILLS_BUNDLE_KEY || "").trim();
  const token = String(process.env.GCS_ACCESS_TOKEN || "").trim();
  if (!bundleKey) {
    throw new Error("SKILLS_BUNDLE_KEY is not set. It is the bundle's only protection and must never be generated here.");
  }
  if (!bundleKey.startsWith(prefix)) throw new Error(`SKILLS_BUNDLE_KEY must sit under ${prefix}; got ${bundleKey}`);
  if (!token && !dryRun) throw new Error("GCS_ACCESS_TOKEN is not set.");

  const { packages, problems } = await findPackages(root);
  for (const p of problems) console.error(`[skills] ${p}`);
  if (problems.length) throw new Error(`${problems.length} package(s) are not publishable; fix them or remove them.`);
  if (!packages.length) throw new Error("No skill packages found. Expected <platform>/<name>/SKILL.md.");

  // A dry run still lists the bucket when it has a token: "29 changed" is
  // worthless if it only means "we did not look". Without one it reports
  // everything as changed and says so.
  const existing = token ? await listObjects({ bucket, prefix, token }) : new Map();
  if (dryRun && !token) console.log("[skills] no GCS_ACCESS_TOKEN: cannot tell which skills already match the bucket.");
  const publishedAt = new Date().toISOString();
  const entries = [];
  let uploaded = 0;
  let unchanged = 0;

  for (const pkg of packages) {
    const base = `${prefix}${pkg.platform}/${pkg.name}`;
    const zip = zipSkillPackage(pkg.name, pkg.files);
    const zipKey = `${base}.zip`;
    const sidecarKey = `${base}.json`;
    const sidecar = {
      name: pkg.name,
      platform: pkg.platform,
      description: pkg.description,
      version: pkg.version,
      gsUri: `gs://${bucket}/${zipKey}`,
      url: `${publicBaseUrl}/${zipKey}`,
      sidecarGsUri: `gs://${bucket}/${sidecarKey}`,
      sidecarUrl: `${publicBaseUrl}/${sidecarKey}`,
      publishedAt,
    };
    entries.push({
      name: pkg.name,
      platform: pkg.platform,
      description: pkg.description,
      version: pkg.version,
      publishedAt,
      zip: sidecar.url,
      image: "",
      sidecar: sidecar.sidecarUrl,
      github: "",
    });

    // Identical bytes mean nothing to do. Re-uploading would only churn the
    // object's generation and its cache entry.
    if (existing.get(zipKey) === md5(zip)) {
      unchanged += 1;
      console.log(`[skills] unchanged ${pkg.platform}/${pkg.name}`);
      continue;
    }
    uploaded += 1;
    console.log(`[skills] ${dryRun ? "would upload" : "uploading"} ${zipKey} (${(zip.length / 1024).toFixed(0)}KB)`);
    if (dryRun) continue;
    await upload({ bucket, object: zipKey, body: zip, contentType: "application/zip", cacheControl: ASSET_CACHE_CONTROL, token });
    await upload({
      bucket,
      object: sidecarKey,
      body: Buffer.from(`${JSON.stringify(sidecar, null, 2)}\n`, "utf8"),
      contentType: "application/json; charset=utf-8",
      cacheControl: HTML_CACHE_CONTROL,
      token,
    });
  }

  // The repository is the catalogue: rebuild it whole rather than upserting,
  // so a package deleted here disappears from the index too.
  entries.sort((a, b) => a.platform.localeCompare(b.platform) || a.name.localeCompare(b.name));
  const index = Buffer.from(`${JSON.stringify({ updatedAt: publishedAt, skills: entries }, null, 2)}\n`, "utf8");
  const indexKey = `${prefix}index.json`;

  // One archive of everything, at the key the gate already knows.
  //
  // Entries are flat -- `<name>/<file>`, with no platform segment -- because a
  // Claude skill installs into `.claude/skills/<name>/`, so the folders in the
  // archive are what the reader drags across. A `claude/` wrapper would add an
  // unwrapping step to every download. The cost is that two platforms cannot
  // both ship a skill of the same name, which is an error rather than a
  // silently overwritten entry.
  const bundleEntries = [];
  const bundledFrom = new Map();
  for (const pkg of packages) {
    const clash = bundledFrom.get(pkg.name);
    if (clash) {
      throw new Error(
        `Both ${clash} and ${pkg.platform} have a skill named "${pkg.name}", which the flat bundle cannot hold. Rename one.`
      );
    }
    bundledFrom.set(pkg.name, pkg.platform);
    for (const f of pkg.files) bundleEntries.push({ name: `${pkg.name}/${f.path}`, data: f.data });
  }
  bundleEntries.sort((a, b) => (a.name < b.name ? -1 : a.name > b.name ? 1 : 0));
  const bundle = zipBuffers(bundleEntries);

  console.log(`[skills] ${packages.length} packages — ${uploaded} changed, ${unchanged} unchanged`);
  console.log(`[skills] ${dryRun ? "would write" : "writing"} ${indexKey} and ${bundleKey} (${(bundle.length / 1024).toFixed(0)}KB)`);
  if (dryRun) {
    console.log(JSON.stringify({ dryRun: true, bucket, packages: packages.length, index: indexKey, bundle: bundleKey }));
    return;
  }
  await upload({ bucket, object: indexKey, body: index, contentType: "application/json; charset=utf-8", cacheControl: HTML_CACHE_CONTROL, token });
  if (existing.get(bundleKey) !== md5(bundle)) {
    await upload({ bucket, object: bundleKey, body: bundle, contentType: "application/zip", cacheControl: ASSET_CACHE_CONTROL, token });
  }
  console.log(JSON.stringify({ bucket, packages: packages.length, uploaded, unchanged, index: indexKey, bundle: bundleKey }));
}

// Only when run as a program. Imported (by the engine's drift test) it must
// define functions and do nothing else.
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch((err) => {
    console.error(`[skills] ${err instanceof Error ? err.message : String(err)}`);
    process.exit(1);
  });
}
