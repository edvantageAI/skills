---
name: youtube-lecture-processor
description: Process YouTube videos to extract transcripts, keyframes, and create study notes. Supports VideoRAG for Q&A on video content. Outputs to HTML, DOCX, or Google Docs.
---

# YouTube Lecture Processor

Process lecture videos into comprehensive study notes with synchronized transcripts and keyframe screenshots.

## Features

- **Smart Keyframe Extraction** - Scene detection + time-based fallback
- **Automatic Transcription** - VTT/SRT format with timestamps
- **1:1 Alignment** - Transcript segments matched to keyframes
- **Multiple Formats** - HTML, DOCX, or Google Docs output
- **VideoRAG Q&A** - Ask questions about video content
- **One Command** - Full pipeline automation

## Quick Start

### One-Command Processing

```bash
python scripts/process_video.py "https://youtube.com/watch?v=..." output_notes
```

This downloads the video, extracts keyframes, generates transcript, aligns them, and creates an HTML document.

**Output:** `output/output_notes.html`

### View Result

```bash
open output/output_notes.html  # macOS
xdg-open output/output_notes.html  # Linux
```

### Manual Step-by-Step

For more control, see [Document Generation Workflow](docs/workflows/document-generation.md).

## Q&A Mode (VideoRAG)

Ask questions about video content:

```bash
# Index videos
python scripts/video_qa.py --index lecture1.mp4 --working-dir ./qa-index

# Ask questions
python scripts/video_qa.py --working-dir ./qa-index --interactive
```

See [VideoRAG Q&A Guide](docs/workflows/videorag-qa.md) for details.

## Installation

```bash
pip install -r requirements.txt
```

See [Installation Guide](docs/installation.md) for complete setup including optional components (Google Docs, VideoRAG).

## Configuration

Customize behavior via `config.yaml`:

```yaml
keyframe_extraction:
  scene_threshold: 30.0        # Scene change sensitivity
  interval_seconds: 10         # Fallback interval

document_generation:
  default_format: html         # html, docx, or gdoc
```

See [Configuration Reference](docs/configuration.md) for all options.

## Documentation

- **[Quickstart Guide](docs/quickstart.md)** - Get started in 5 minutes
- **[Installation](docs/installation.md)** - Complete setup instructions
- **[Configuration](docs/configuration.md)** - Customize settings
- **[Document Generation](docs/workflows/document-generation.md)** - Full workflow guide
- **[VideoRAG Q&A](docs/workflows/videorag-qa.md)** - Ask questions about videos
- **[API Reference](docs/api-reference.md)** - Complete script parameters
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions
- **[Google Docs Setup](docs/google-docs-setup.md)** - API credentials guide

## Common Use Cases

### Process YouTube Lecture to HTML

```bash
python scripts/process_video.py "https://youtube.com/watch?v=..." lecture_notes
```

### Create DOCX from Local Video

```bash
python scripts/process_video.py video.mp4 notes --format docx
```

### Batch Process Multiple Videos

```bash
for url in $(cat video_urls.txt); do
  name=$(basename "$url" | cut -d'=' -f2)
  python scripts/process_video.py "$url" "lecture_$name"
done
```

### Q&A on Course Lectures

```bash
# Index all lectures
python scripts/video_qa.py --index lecture*.mp4 --working-dir ./course

# Interactive Q&A
python scripts/video_qa.py --working-dir ./course --interactive
```

## Requirements

- Python 3.11+
- OpenCV (`opencv-python`)
- yt-dlp
- PyYAML

**Optional:**
- `python-docx` - DOCX output
- Google API libraries - Google Docs output
- VideoRAG - Q&A functionality

See [Installation Guide](docs/installation.md) for details.

## Project Structure

```
youtube-lecture-processor/
├── scripts/
│   ├── process_video.py           # Unified workflow (use this!)
│   ├── extract_keyframes.py       # Extract keyframes from video
│   ├── align_transcript_keyframes.py  # Align transcript to keyframes
│   ├── create_document.py         # Generate HTML/DOCX/GDoc
│   └── video_qa.py                # VideoRAG Q&A mode
├── docs/                          # Complete documentation
├── config.yaml                    # Configuration file
├── requirements.txt               # Python dependencies
└── README.md                      # Project overview
```

## Support

- **Documentation:** See [docs/](docs/) directory
- **Issues:** Report bugs at repository issues page
- **Help:** Add `--help` to any script for usage information

## License

MIT
