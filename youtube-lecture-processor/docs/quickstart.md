# Quickstart Guide

Get up and running with YouTube Lecture Processor in 5 minutes.

## Prerequisites

- Python 3.11+ installed
- Basic command line knowledge

## Installation

```bash
cd youtube-lecture-processor
pip install -r requirements.txt
```

## Process Your First Video

### Option 1: One Command (Recommended)

Process a YouTube video in a single command:

```bash
python scripts/process_video.py "https://youtube.com/watch?v=VIDEO_ID" my_notes
```

This will:
1. Download the video and transcript
2. Extract keyframes
3. Align transcript with keyframes
4. Generate an HTML document

View the result:

```bash
open output/my_notes.html  # macOS
xdg-open output/my_notes.html  # Linux
start output/my_notes.html  # Windows
```

### Option 2: Step by Step

For more control, run each step manually:

**1. Download video** (skip if you have a local file):

```bash
yt-dlp -f "best[ext=mp4]" -o video.mp4 "https://youtube.com/watch?v=VIDEO_ID"
```

**2. Extract keyframes:**

```bash
python scripts/extract_keyframes.py video.mp4 keyframes/
```

**3. Get transcript** (if available):

```bash
yt-dlp --write-auto-sub --sub-format vtt --skip-download -o transcript "https://youtube.com/watch?v=VIDEO_ID"
```

**4. Align transcript with keyframes:**

```bash
python scripts/align_transcript_keyframes.py transcript.en.vtt keyframes/keyframes_metadata.json aligned.json
```

**5. Create document:**

```bash
python scripts/create_document.py aligned.json output.html --format html
```

## Try Different Formats

### Create a DOCX document:

```bash
python scripts/process_video.py "https://youtube.com/watch?v=VIDEO_ID" notes --format docx
```

### Create a Google Doc:

First, set up [Google API credentials](google-docs-setup.md), then:

```bash
python scripts/process_video.py "https://youtube.com/watch?v=VIDEO_ID" notes --format gdoc --credentials google-credentials.json
```

## Customize Settings

Edit `config.yaml` to change defaults:

```yaml
keyframe_extraction:
  scene_threshold: 30.0    # Increase for fewer keyframes
  interval_seconds: 10     # Increase for fewer keyframes

document_generation:
  default_format: docx     # Change default output format
```

## Q&A Mode (VideoRAG)

If you have VideoRAG installed:

**Index a video:**

```bash
python scripts/video_qa.py --index lecture.mp4 --working-dir ./qa-index
```

**Ask questions:**

```bash
python scripts/video_qa.py --working-dir ./qa-index --interactive
```

Type your questions and get answers based on video content!

## Next Steps

- [Full Installation Guide](installation.md) - Complete setup instructions
- [Configuration Reference](configuration.md) - All configuration options
- [Document Generation Workflow](workflows/document-generation.md) - Detailed workflow guide
- [VideoRAG Q&A Guide](workflows/videorag-qa.md) - Complete Q&A setup
- [Troubleshooting](troubleshooting.md) - Common issues and solutions

## Tips

- Use `--keep-intermediate` to inspect intermediate files
- Adjust `--scene-threshold` for videos with frequent/rare transitions
- Use `--interval` to control minimum time between keyframes
- Add `--help` to any script to see all options
