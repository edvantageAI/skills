# Configuration Reference

The `config.yaml` file allows you to customize default behavior for all scripts.

## Configuration File Location

Default location: `youtube-lecture-processor/config.yaml`

Override with `--config` flag:

```bash
python scripts/process_video.py video.mp4 output --config my_config.yaml
```

## Complete Configuration

```yaml
# YouTube Lecture Processor Configuration

keyframe_extraction:
  scene_threshold: 30.0        # Scene change sensitivity (20-50)
  interval_seconds: 10         # Fallback interval when no scene changes
  output_format: jpg           # jpg or png

document_generation:
  default_format: html         # html, docx, or gdoc
  html:
    embed_images: true         # Base64 embed vs file references
  docx:
    image_width_inches: 3.0

videorag:
  default_llm: openai
  models:
    openai: gpt-4o-mini
    anthropic: claude-3-5-sonnet-20241022
    gemini: gemini-1.5-flash
    ollama: llama3.1:8b

paths:
  working_dir: ./working       # Default working directory
  output_dir: ./output         # Default output directory
```

## Settings Explained

### Keyframe Extraction

#### `scene_threshold` (float, default: 30.0)

Controls sensitivity to scene changes. Range: 20-50

- **Lower values (20-25)**: More sensitive, extracts more keyframes
- **Medium values (30-35)**: Balanced, good for most lectures
- **Higher values (40-50)**: Less sensitive, fewer keyframes

**When to adjust:**
- Slide presentations: Use 25-30 (detect slide transitions)
- Software demos: Use 35-40 (ignore minor cursor movements)
- Mixed content: Use 30 (default)

#### `interval_seconds` (int, default: 10)

Fallback interval when no scene changes are detected.

- **Shorter (5-7s)**: More comprehensive coverage
- **Medium (10-15s)**: Balanced approach
- **Longer (20-30s)**: Highlight key moments only

#### `output_format` (string, default: 'jpg')

Image format for keyframes.

- `jpg`: Smaller file size, good quality
- `png`: Lossless, larger files, better for text-heavy slides

### Document Generation

#### `default_format` (string, default: 'html')

Default output format. Options: `html`, `docx`, `gdoc`

- `html`: Fast, self-contained, works everywhere
- `docx`: Editable in Word, good for sharing
- `gdoc`: Cloud-based, collaborative editing

#### `html.embed_images` (boolean, default: true)

Whether to embed images as base64 in HTML.

- `true`: Single-file output, portable
- `false`: Separate image files, smaller HTML

#### `docx.image_width_inches` (float, default: 3.0)

Width of images in DOCX documents (in inches).

- Smaller (2.0-2.5): More text visible
- Medium (3.0-3.5): Balanced
- Larger (4.0-5.0): Emphasize visuals

### VideoRAG

#### `default_llm` (string, default: 'openai')

Default LLM provider for Q&A. Options: `openai`, `anthropic`, `gemini`, `ollama`

#### `models`

Default model for each provider:

- **openai**: `gpt-4o-mini` (fast, cost-effective)
- **anthropic**: `claude-3-5-sonnet-20241022` (high quality)
- **gemini**: `gemini-1.5-flash` (fast, multimodal)
- **ollama**: `llama3.1:8b` (local, free)

### Paths

#### `working_dir` (string, default: './working')

Directory for intermediate files (keyframes, transcripts, etc.).

#### `output_dir` (string, default: './output')

Directory for final output documents.

## Environment Variables

Some settings can be overridden with environment variables:

```bash
# API keys for LLM providers
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_API_KEY="..."
```

## Command-Line Overrides

All config settings can be overridden via command-line flags:

```bash
# Override scene threshold
python scripts/extract_keyframes.py video.mp4 keyframes/ --scene-threshold 40

# Override output format
python scripts/process_video.py video.mp4 output --format docx

# Override LLM provider
python scripts/video_qa.py --working-dir ./qa --llm anthropic
```

**Priority order:**
1. Command-line flags (highest)
2. Custom config file (--config)
3. Default config.yaml
4. Hard-coded defaults (lowest)

## Configuration Presets

### For Slide Presentations

```yaml
keyframe_extraction:
  scene_threshold: 25.0
  interval_seconds: 15
  output_format: png

document_generation:
  default_format: docx
  docx:
    image_width_inches: 4.0
```

### For Software Demonstrations

```yaml
keyframe_extraction:
  scene_threshold: 40.0
  interval_seconds: 10
  output_format: jpg

document_generation:
  default_format: html
  html:
    embed_images: true
```

### For Mixed Content Lectures

```yaml
keyframe_extraction:
  scene_threshold: 30.0
  interval_seconds: 12
  output_format: jpg

document_generation:
  default_format: html
```

## Next Steps

- [Quickstart Guide](quickstart.md) - Get started quickly
- [Document Generation Workflow](workflows/document-generation.md) - Detailed workflow
- [Troubleshooting](troubleshooting.md) - Common issues
