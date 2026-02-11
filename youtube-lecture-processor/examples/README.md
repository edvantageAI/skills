# Examples

Example scripts and configurations for common use cases.

## Batch Processing Script

Process multiple YouTube videos at once.

### Usage

1. **Create video list:**

Create `video_urls.txt` in the project root:

```
https://youtube.com/watch?v=VIDEO_ID_1
https://youtube.com/watch?v=VIDEO_ID_2
https://youtube.com/watch?v=VIDEO_ID_3
# Comments are allowed
https://youtube.com/watch?v=VIDEO_ID_4
```

2. **Run batch script:**

```bash
bash examples/batch_process.sh
```

3. **Find output:**

All processed files will be in `batch_output/` directory.

## Configuration Examples

Pre-configured settings for different video types.

### Lecture Slides (`lecture_slides.yaml`)

**Best for:**
- PowerPoint/Keynote presentations
- Slide-heavy lectures
- Conference talks

**Settings:**
- High sensitivity to detect slide transitions
- PNG format for text clarity
- DOCX output for professional documents

**Usage:**
```bash
python scripts/process_video.py video.mp4 output \
  --config examples/config_examples/lecture_slides.yaml
```

### Demo Videos (`demo_video.yaml`)

**Best for:**
- Coding tutorials
- Software walkthroughs
- Screen recordings

**Settings:**
- Lower sensitivity to ignore cursor movement
- JPG format for smaller files
- HTML output for quick sharing

**Usage:**
```bash
python scripts/process_video.py video.mp4 output \
  --config examples/config_examples/demo_video.yaml
```

### Mixed Content (`mixed_content.yaml`)

**Best for:**
- Lectures mixing slides and demos
- Videos with varied pacing
- General-purpose processing

**Settings:**
- Balanced sensitivity
- JPG format
- HTML output with embedded images

**Usage:**
```bash
python scripts/process_video.py video.mp4 output \
  --config examples/config_examples/mixed_content.yaml
```

## Creating Custom Configurations

Copy one of the example configs and modify:

```bash
cp examples/config_examples/mixed_content.yaml my_config.yaml
# Edit my_config.yaml
python scripts/process_video.py video.mp4 output --config my_config.yaml
```

## Tips

### Batch Processing
- Test on one video first to verify settings
- Use `--keep-intermediate` for the first run to inspect results
- Monitor disk space for large batches

### Custom Configurations
- Start with an example config closest to your use case
- Adjust `scene_threshold` incrementally (±5)
- Test with a short video clip first

### Performance
- Use SSD storage for faster processing
- Process multiple videos in parallel on multi-core systems
- Consider cloud processing for large batches

## Next Steps

- [Document Generation Workflow](../docs/workflows/document-generation.md)
- [Configuration Reference](../docs/configuration.md)
- [Troubleshooting Guide](../docs/troubleshooting.md)
