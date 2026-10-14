# Document Generation Workflow

Complete guide to generating study notes from lecture videos.

## Overview

The workflow consists of four main steps:

1. **Video Acquisition** - Download or use local video
2. **Keyframe Extraction** - Extract screenshots at key moments
3. **Transcript Alignment** - Match transcript text to keyframes
4. **Document Generation** - Create final output

## Quick Start

Use the unified workflow script:

```bash
python scripts/process_video.py "https://youtube.com/watch?v=VIDEO_ID" output_name
```

## Detailed Step-by-Step

### Step 1: Video Acquisition

#### From YouTube

```bash
yt-dlp -f "best[ext=mp4]" -o video.mp4 "https://youtube.com/watch?v=VIDEO_ID"
```

**Get transcript:**

```bash
yt-dlp --write-auto-sub --sub-format vtt --skip-download -o transcript "https://youtube.com/watch?v=VIDEO_ID"
```

This creates `transcript.en.vtt` (or similar, depending on language).

#### From Local File

If you already have a video file, skip this step.

For transcripts, you can:
- Create manually in VTT format
- Use speech-to-text tools
- Skip (document will have empty transcript fields)

### Step 2: Keyframe Extraction

Extract key screenshots from the video:

```bash
python scripts/extract_keyframes.py video.mp4 keyframes/
```

**Options:**

```bash
python scripts/extract_keyframes.py video.mp4 keyframes/ \
  --scene-threshold 30.0 \
  --interval 10 \
  --format jpg
```

**Parameters:**
- `--scene-threshold`: Scene change sensitivity (20-50, default: 30)
- `--interval`: Fallback interval in seconds (default: 10)
- `--format`: Output format (jpg or png, default: jpg)

**Output:**
- `keyframes/keyframe_0000_t0.00s.jpg` - Individual keyframe images
- `keyframes/keyframe_0001_t15.32s.jpg`
- ...
- `keyframes/keyframes_metadata.json` - Metadata with timestamps

**Tuning:**

For slide presentations (frequent scene changes):
```bash
python scripts/extract_keyframes.py slides_lecture.mp4 keyframes/ --scene-threshold 25
```

For demos with subtle changes:
```bash
python scripts/extract_keyframes.py demo.mp4 keyframes/ --scene-threshold 40
```

### Step 3: Transcript Alignment

Align transcript segments with keyframes:

```bash
python scripts/align_transcript_keyframes.py transcript.en.vtt keyframes/keyframes_metadata.json aligned.json
```

This creates `aligned.json` with structure:

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
        "filepath": "keyframes/keyframe_0000_t0.00s.jpg"
      },
      "transcript": "Welcome to the lecture on..."
    },
    ...
  ]
}
```

**Without Transcript:**

If no transcript is available, create a minimal JSON manually:

```json
{
  "video_info": {
    "video_path": "video.mp4",
    "duration": 0,
    "fps": 0
  },
  "aligned_items": []
}
```

### Step 4: Document Generation

Create the final document in your preferred format.

#### HTML (Recommended for Quick Review)

```bash
python scripts/create_document.py aligned.json output.html --format html
```

**Features:**
- Self-contained (embedded images)
- Works in any browser
- Styled table with timestamps
- Searchable text

**View:**
```bash
open output.html  # macOS
```

#### DOCX (Editable, Shareable)

```bash
python scripts/create_document.py aligned.json output.docx --format docx
```

**Options:**

```bash
python scripts/create_document.py aligned.json output.docx \
  --format docx \
  --image-width 3.5
```

**Features:**
- Editable in Microsoft Word / LibreOffice
- Professional formatting
- Adjustable image sizes
- Easy to share

#### Google Docs (Collaborative)

First, set up [Google API credentials](../google-docs-setup.md).

```bash
python scripts/create_document.py aligned.json output_gdoc.json \
  --format gdoc \
  --credentials google-credentials.json
```

**Output:**
Creates `output_gdoc.json` with:
```json
{
  "doc_id": "...",
  "doc_url": "https://docs.google.com/document/d/.../"
}
```

Open the `doc_url` in your browser to view and edit the Google Doc.

**Features:**
- Cloud-based storage
- Real-time collaboration
- Automatic saving
- Accessible anywhere

## Advanced Usage

### Batch Processing

Process multiple videos:

```bash
for url in $(cat video_urls.txt); do
  name=$(echo "$url" | md5sum | cut -d' ' -f1)
  python scripts/process_video.py "$url" "$name"
done
```

### Custom Configuration

Create a custom config for specific use cases:

**lecture_config.yaml:**
```yaml
keyframe_extraction:
  scene_threshold: 25.0
  interval_seconds: 15

document_generation:
  default_format: docx
  docx:
    image_width_inches: 4.0
```

Use it:
```bash
python scripts/process_video.py video.mp4 output --config lecture_config.yaml
```

### Processing Local Videos Without Transcripts

```bash
python scripts/process_video.py my_video.mp4 output_notes
```

The script will:
1. Extract keyframes
2. Create aligned data with empty transcripts
3. Generate document with screenshots only

You can manually add notes to the document later.

### Keep Intermediate Files

For inspection or debugging:

```bash
python scripts/process_video.py video.mp4 output --keep-intermediate
```

This preserves:
- Downloaded video
- Keyframe images
- Transcript file
- Aligned JSON

## Tips & Best Practices

### Keyframe Extraction

- **Test scene threshold:** Start with default (30), adjust based on results
- **Check keyframes directory:** Review extracted images before proceeding
- **Balance quality and quantity:** More keyframes = more detail, but larger documents

### Transcript Alignment

- **Verify transcript quality:** Some auto-generated transcripts have errors
- **Manual corrections:** Edit VTT file if needed before alignment
- **Multiple languages:** YouTube provides transcripts in various languages

### Document Generation

- **Start with HTML:** Fastest, easiest to review
- **Use DOCX for sharing:** More professional, editable
- **Google Docs for collaboration:** Best for team note-taking

### Storage

- **Cleanup:** Delete intermediate files after successful generation
- **Archive:** Keep `aligned.json` for regenerating documents
- **Backup:** Store original video URLs in a text file

## Troubleshooting

See [Troubleshooting Guide](../troubleshooting.md) for common issues and solutions.

## Next Steps

- [VideoRAG Q&A Workflow](videorag-qa.md) - Ask questions about videos
- [API Reference](../api-reference.md) - Complete script parameters
- [Configuration Reference](../configuration.md) - Customize settings
