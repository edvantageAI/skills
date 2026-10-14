# YouTube Lecture Processor

> Transform lecture videos into comprehensive study notes with synchronized transcripts and screenshots.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

✨ **Smart Keyframe Extraction** - Scene detection + time-based fallback
📝 **Automatic Transcription** - VTT/SRT format with timestamps
🔗 **1:1 Alignment** - Transcript segments matched to keyframes
📄 **Multiple Formats** - HTML, DOCX, or Google Docs output
🤖 **VideoRAG Q&A** - Ask questions about video content
🎯 **One Command** - Full pipeline automation

## Quick Start

### Installation

```bash
cd youtube-lecture-processor
pip install -r requirements.txt
```

### Process a Video

```bash
python scripts/process_video.py "https://youtube.com/watch?v=VIDEO_ID" my_notes
```

### View Output

```bash
open output/my_notes.html  # macOS
xdg-open output/my_notes.html  # Linux
start output\my_notes.html  # Windows
```

## What It Does

```
YouTube Video
     ↓
  Download
     ↓
Extract Keyframes → Align with Transcript → Generate Document
     ↓                      ↓                       ↓
 Screenshots         Timestamped Text         HTML/DOCX/GDoc
```

**Result:** A formatted document with:
- Screenshots of key moments
- Synchronized transcript text
- Timestamps for navigation
- Professional styling

## Use Cases

### 📚 Students
Create comprehensive study notes from lecture videos

### 👨‍💼 Professionals
Document software demonstrations and training videos

### 🎓 Educators
Generate materials for course content

### 🔬 Researchers
Extract and analyze presentation content

### 💼 Content Creators
Repurpose video content into written formats

## Examples

### Process YouTube Lecture

```bash
python scripts/process_video.py \
  "https://youtube.com/watch?v=dQw4w9WgXcQ" \
  machine_learning_intro
```

### Create DOCX from Local Video

```bash
python scripts/process_video.py video.mp4 notes --format docx
```

### Generate Google Doc

```bash
python scripts/process_video.py \
  "https://youtube.com/watch?v=..." \
  notes \
  --format gdoc \
  --credentials google-credentials.json
```

### Ask Questions About Videos (VideoRAG)

```bash
# Index videos
python scripts/video_qa.py --index lecture.mp4 --working-dir ./qa-index

# Interactive Q&A
python scripts/video_qa.py --working-dir ./qa-index --interactive
```

## Documentation

📖 **[Complete Documentation](docs/)** - All guides and references

**Quick Links:**
- [Quickstart Guide](docs/quickstart.md) - Get started in 5 minutes
- [Installation Guide](docs/installation.md) - Detailed setup instructions
- [Configuration Reference](docs/configuration.md) - Customize behavior
- [Document Generation Workflow](docs/workflows/document-generation.md) - Step-by-step guide
- [VideoRAG Q&A Guide](docs/workflows/videorag-qa.md) - Ask questions about videos
- [API Reference](docs/api-reference.md) - Complete parameter documentation
- [Troubleshooting](docs/troubleshooting.md) - Common issues and solutions

## Requirements

**System:**
- Python 3.11 or higher
- [Git LFS](https://git-lfs.github.com/) (`brew install git-lfs`)

**Core Python packages:**
- opencv-python
- yt-dlp
- PyYAML

**Optional:**
- python-docx (for DOCX output)
- Google API libraries (for Google Docs)
- VideoRAG (for Q&A functionality)

See [Installation Guide](docs/installation.md) for complete setup.

## Configuration

Customize behavior via `config.yaml`:

```yaml
keyframe_extraction:
  scene_threshold: 30.0        # Scene change sensitivity (20-50)
  interval_seconds: 10         # Fallback interval

document_generation:
  default_format: html         # html, docx, or gdoc
  docx:
    image_width_inches: 3.0

videorag:
  default_llm: openai
  models:
    openai: gpt-4o-mini
    anthropic: claude-3-5-sonnet-20241022
```

See [Configuration Reference](docs/configuration.md) for all options.

## Output Formats

### HTML (Default)
- Self-contained single file
- Embedded images
- Works in any browser
- Searchable text
- No external dependencies

### DOCX
- Editable in Word/LibreOffice
- Professional formatting
- Adjustable image sizes
- Easy to share

### Google Docs
- Cloud-based storage
- Real-time collaboration
- Automatic saving
- Accessible anywhere

## Advanced Usage

### Batch Processing

```bash
for url in $(cat video_urls.txt); do
  name=$(basename "$url" | cut -d'=' -f2)
  python scripts/process_video.py "$url" "lecture_$name"
done
```

### Custom Configuration

```bash
python scripts/process_video.py video.mp4 output \
  --scene-threshold 40 \
  --interval 15 \
  --format docx \
  --image-width 4.0
```

### Keep Intermediate Files

```bash
python scripts/process_video.py video.mp4 output --keep-intermediate
```

Preserves:
- Downloaded video
- Keyframe images
- Transcript file
- Aligned JSON data

## Project Structure

```
youtube-lecture-processor/
├── scripts/
│   ├── process_video.py           # 🎯 Unified workflow (use this!)
│   ├── extract_keyframes.py       # Extract keyframes from video
│   ├── align_transcript_keyframes.py  # Align transcript to keyframes
│   ├── create_document.py         # Generate HTML/DOCX/GDoc
│   ├── video_qa.py                # VideoRAG Q&A mode
│   └── exceptions.py              # Custom exceptions
├── docs/                          # 📚 Complete documentation
│   ├── installation.md
│   ├── quickstart.md
│   ├── configuration.md
│   ├── troubleshooting.md
│   ├── api-reference.md
│   ├── google-docs-setup.md
│   └── workflows/
│       ├── document-generation.md
│       └── videorag-qa.md
├── examples/                      # 💡 Example scripts
├── tests/                         # 🧪 Unit tests
├── config.yaml                    # ⚙️ Configuration file
├── requirements.txt               # 📦 Python dependencies
├── requirements-dev.txt           # 🔧 Development dependencies
├── setup.py                       # 📦 Package setup
├── .gitignore                     # 🚫 Git ignore rules
├── SKILL.md                       # 🤖 Claude Code skill definition
└── README.md                      # 📖 This file
```

## How It Works

### 1. Keyframe Extraction
- Analyzes video frames for scene changes
- Uses adaptive threshold detection
- Falls back to time-based intervals
- Saves metadata with timestamps

### 2. Transcript Alignment
- Parses VTT/SRT subtitle files
- Matches transcript segments to keyframes
- Creates 1:1 mapping based on timestamps
- Handles missing transcripts gracefully

### 3. Document Generation
- Creates formatted table layout
- Embeds or references images
- Adds timestamps and navigation
- Supports multiple output formats

### 4. VideoRAG Q&A (Optional)
- Indexes video content for semantic search
- Enables natural language queries
- Returns answers with video references
- Supports multiple LLM providers

## Tips & Best Practices

### Keyframe Extraction
- **Slide presentations:** Use lower threshold (25-30)
- **Software demos:** Use higher threshold (35-40)
- **Mixed content:** Stick with default (30)

### Performance
- Use SSD storage for faster processing
- Adjust `--interval` to control keyframe density
- Consider `--format jpg` for smaller file sizes

### Workflow
- Start with HTML for quick review
- Use DOCX for sharing and editing
- Use Google Docs for team collaboration

## Troubleshooting

**Common Issues:**

- **No keyframes extracted:** Lower `--scene-threshold`
- **Too many keyframes:** Increase `--scene-threshold` or `--interval`
- **Import errors:** Run `pip install -r requirements.txt`
- **Video not found:** Check file path or URL

See [Troubleshooting Guide](docs/troubleshooting.md) for complete solutions.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Support

- **Documentation:** [docs/](docs/) directory
- **Issues:** Report bugs via GitHub issues
- **Help:** Run any script with `--help` flag

## License

MIT License - see LICENSE file for details

## Acknowledgments

- [OpenCV](https://opencv.org/) - Computer vision library
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube downloader
- [VideoRAG](https://github.com/HKUDS/VideoRAG) - Video Q&A framework
- [python-docx](https://python-docx.readthedocs.io/) - DOCX generation

---

**Made with ❤️ for learners and educators**
