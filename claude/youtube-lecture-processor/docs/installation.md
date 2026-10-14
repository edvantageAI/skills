# Installation Guide

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git (for cloning repositories)

## Basic Installation

### 1. Install Core Dependencies

```bash
cd youtube-lecture-processor
pip install -r requirements.txt
```

This installs:
- `opencv-python` - Video processing and keyframe extraction
- `yt-dlp` - YouTube video downloading
- `pyyaml` - Configuration file support
- `python-docx` - DOCX document generation
- Google API libraries (for Google Docs support)

### 2. Verify Installation

```bash
python scripts/extract_keyframes.py --help
```

If you see the help message, the basic installation is complete!

## Optional: Google Docs Support

To create Google Docs, you need API credentials:

1. Follow the guide in [google-docs-setup.md](google-docs-setup.md)
2. Download your credentials JSON file
3. Save it as `google-credentials.json` in the project root

## Optional: VideoRAG for Q&A

VideoRAG enables asking questions about video content.

### Requirements

- PyTorch (CUDA GPU recommended for performance)
- Additional dependencies (transformers, accelerate, moviepy)

### Installation Steps

1. **Clone VideoRAG repository:**

```bash
cd ..  # Go to parent directory
git clone https://github.com/HKUDS/VideoRAG.git
cd VideoRAG
```

2. **Follow VideoRAG installation instructions:**

See `VideoRAG-algorithm/README.md` in the cloned repository.

3. **Install VideoRAG in your environment:**

```bash
# From VideoRAG directory
cd VideoRAG-algorithm
pip install -e .
```

4. **Verify VideoRAG installation:**

```bash
python -c "import videorag; print('VideoRAG installed successfully')"
```

## Platform-Specific Notes

### macOS

All dependencies should work out of the box. If you encounter issues with OpenCV:

```bash
brew install opencv
pip install --upgrade opencv-python
```

### Linux

Install system dependencies:

```bash
# Ubuntu/Debian
sudo apt-get install python3-opencv

# Fedora/RHEL
sudo dnf install python3-opencv
```

### Windows

Download and install from official sources:
- Python: https://www.python.org/downloads/windows/
- Visual C++ Redistributable (required for OpenCV)

## Development Installation

For development work:

```bash
pip install -r requirements-dev.txt
```

This adds:
- pytest - Testing framework
- black - Code formatter
- flake8 - Linting
- mypy - Type checking

## Troubleshooting

### Import Errors

If you get import errors, ensure you're in the correct directory and your virtual environment is activated.

### OpenCV Issues

If OpenCV fails to import:

```bash
pip uninstall opencv-python opencv-python-headless
pip install opencv-python==4.8.1.78
```

### yt-dlp Issues

Update to the latest version:

```bash
pip install --upgrade yt-dlp
```

### Permission Errors

On macOS/Linux, scripts may need execute permissions:

```bash
chmod +x scripts/*.py
```

## Next Steps

- [Quickstart Guide](quickstart.md) - Get started in 5 minutes
- [Configuration](configuration.md) - Customize settings
