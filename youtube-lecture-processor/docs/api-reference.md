# API Reference

Complete reference for all script parameters and options.

## process_video.py

Unified workflow script for end-to-end processing.

### Usage

```bash
python scripts/process_video.py INPUT OUTPUT_NAME [OPTIONS]
```

### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `INPUT` | string | Yes | YouTube URL or local video file path |
| `OUTPUT_NAME` | string | Yes | Output name (without extension) |

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--format` | choice | html | Output format: html, docx, or gdoc |
| `--working-dir` | path | ./working | Working directory for intermediate files |
| `--output-dir` | path | ./output | Output directory for final document |
| `--scene-threshold` | float | 30.0 | Scene change threshold (20-50) |
| `--interval` | int | 10 | Keyframe interval in seconds |
| `--keyframe-format` | choice | jpg | Keyframe format: jpg or png |
| `--image-width` | float | 3.0 | Image width in inches (DOCX/GDoc) |
| `--keep-intermediate` | flag | false | Keep intermediate files |
| `--credentials` | path | - | Google API credentials (required for gdoc) |
| `--config` | path | config.yaml | Custom config file |

### Examples

```bash
# Basic usage
python scripts/process_video.py "https://youtube.com/watch?v=..." notes

# Custom settings
python scripts/process_video.py video.mp4 output \
  --format docx \
  --scene-threshold 40 \
  --interval 15

# Google Docs output
python scripts/process_video.py "URL" notes \
  --format gdoc \
  --credentials google-credentials.json
```

## extract_keyframes.py

Extract keyframes from video files.

### Usage

```bash
python scripts/extract_keyframes.py VIDEO_PATH OUTPUT_DIR [OPTIONS]
```

### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `VIDEO_PATH` | path | Yes | Path to input video file |
| `OUTPUT_DIR` | path | Yes | Directory to save keyframes |

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--scene-threshold` | float | 30.0 | Scene change threshold (0-255) |
| `--interval` | int | 10 | Fallback interval in seconds |
| `--format` | choice | jpg | Output format: jpg or png |
| `--config` | path | config.yaml | Custom config file |

### Output

- `OUTPUT_DIR/keyframe_NNNN_tTIME.{jpg|png}` - Keyframe images
- `OUTPUT_DIR/keyframes_metadata.json` - Metadata file

### Examples

```bash
# Basic usage
python scripts/extract_keyframes.py video.mp4 keyframes/

# High sensitivity (more keyframes)
python scripts/extract_keyframes.py video.mp4 keyframes/ --scene-threshold 20

# Low sensitivity (fewer keyframes)
python scripts/extract_keyframes.py video.mp4 keyframes/ --scene-threshold 45

# PNG format
python scripts/extract_keyframes.py video.mp4 keyframes/ --format png
```

## align_transcript_keyframes.py

Align transcript segments with keyframes.

### Usage

```bash
python scripts/align_transcript_keyframes.py TRANSCRIPT KEYFRAMES_METADATA OUTPUT [OPTIONS]
```

### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `TRANSCRIPT` | path | Yes | Path to transcript file (VTT/SRT) |
| `KEYFRAMES_METADATA` | path | Yes | Path to keyframes metadata JSON |
| `OUTPUT` | path | Yes | Path to output aligned JSON |

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--config` | path | config.yaml | Custom config file |

### Input Format

**VTT (WebVTT):**
```
WEBVTT

00:00:00.000 --> 00:00:05.000
First subtitle

00:00:05.000 --> 00:00:10.000
Second subtitle
```

**SRT (SubRip):**
```
1
00:00:00,000 --> 00:00:05,000
First subtitle

2
00:00:05,000 --> 00:00:10,000
Second subtitle
```

### Output Format

```json
{
  "video_info": {
    "video_path": "video.mp4",
    "duration": 1234.56,
    "fps": 30.0
  },
  "aligned_items": [
    {
      "keyframe": {
        "index": 0,
        "timestamp": 0.0,
        "filepath": "keyframes/keyframe_0000.jpg"
      },
      "transcript": "Matching transcript text"
    }
  ]
}
```

### Examples

```bash
# Basic usage
python scripts/align_transcript_keyframes.py \
  transcript.vtt \
  keyframes/keyframes_metadata.json \
  aligned.json
```

## create_document.py

Create final document from aligned data.

### Usage

```bash
python scripts/create_document.py ALIGNED_JSON OUTPUT_PATH [OPTIONS]
```

### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `ALIGNED_JSON` | path | Yes | Path to aligned JSON file |
| `OUTPUT_PATH` | path | Yes | Path for output file |

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--format` | choice | html | Output format: html, docx, or gdoc |
| `--credentials` | path | - | Google API credentials (required for gdoc) |
| `--image-width` | float | 3.0 | Image width in inches (DOCX/GDoc) |
| `--config` | path | config.yaml | Custom config file |

### Examples

```bash
# HTML (default)
python scripts/create_document.py aligned.json output.html

# DOCX
python scripts/create_document.py aligned.json output.docx --format docx

# DOCX with custom image size
python scripts/create_document.py aligned.json output.docx \
  --format docx \
  --image-width 4.0

# Google Docs
python scripts/create_document.py aligned.json output_gdoc.json \
  --format gdoc \
  --credentials google-credentials.json
```

## video_qa.py

Q&A on video content using VideoRAG.

### Usage

```bash
python scripts/video_qa.py --working-dir DIR [OPTIONS]
```

### Required Options

| Option | Description |
|--------|-------------|
| `--working-dir DIR` | Directory for VideoRAG index |

### Operational Modes

Must specify at least one:

| Option | Description |
|--------|-------------|
| `--index VIDEO [VIDEO ...]` | Index video file(s) |
| `--question "TEXT"` | Ask a single question |
| `--interactive` | Enter interactive Q&A mode |

### LLM Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--llm` | choice | openai | Provider: openai, anthropic, gemini, ollama |
| `--model` | string | - | Specific model name |
| `--api-key` | string | - | API key for provider |

### Other Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--no-references` | flag | false | Omit video clip references |
| `--config` | path | config.yaml | Custom config file |

### Examples

```bash
# Index videos
python scripts/video_qa.py \
  --index lecture1.mp4 lecture2.mp4 \
  --working-dir ./qa-index

# Single question
python scripts/video_qa.py \
  --working-dir ./qa-index \
  --question "What is the main topic?"

# Interactive mode
python scripts/video_qa.py \
  --working-dir ./qa-index \
  --interactive

# Use Anthropic Claude
python scripts/video_qa.py \
  --working-dir ./qa-index \
  --llm anthropic \
  --interactive

# Use specific model
python scripts/video_qa.py \
  --working-dir ./qa-index \
  --llm openai \
  --model gpt-4o \
  --question "Summarize the lecture"
```

## Configuration File

All scripts support custom configuration via `config.yaml`.

### Structure

```yaml
keyframe_extraction:
  scene_threshold: 30.0
  interval_seconds: 10
  output_format: jpg

document_generation:
  default_format: html
  html:
    embed_images: true
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
  working_dir: ./working
  output_dir: ./output
```

### Usage

```bash
# Use custom config
python scripts/process_video.py video.mp4 output --config my_config.yaml
```

See [Configuration Reference](configuration.md) for details.

## Environment Variables

### API Keys

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_API_KEY="..."
```

### Debug Mode

```bash
export DEBUG=1
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | File not found |
| 3 | Invalid configuration |

## Next Steps

- [Quickstart Guide](quickstart.md) - Get started quickly
- [Configuration Reference](configuration.md) - Detailed config options
- [Workflows](workflows/) - Complete workflow guides
