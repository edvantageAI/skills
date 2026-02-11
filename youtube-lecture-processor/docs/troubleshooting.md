# Troubleshooting Guide

Common issues and their solutions.

## Installation Issues

### ModuleNotFoundError: No module named 'cv2'

**Problem:** OpenCV not installed correctly.

**Solution:**

```bash
pip uninstall opencv-python opencv-python-headless
pip install opencv-python==4.8.1.78
```

### yt-dlp command not found

**Problem:** yt-dlp not in PATH.

**Solution:**

```bash
pip install --upgrade yt-dlp
```

If still not working:

```bash
python -m yt_dlp --help
```

### ImportError: google.auth

**Problem:** Google API libraries not installed.

**Solution:**

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## Keyframe Extraction Issues

### No keyframes extracted

**Symptoms:**
- `keyframes/` directory is empty or has very few images
- Script completes but no useful keyframes

**Solutions:**

1. **Lower scene threshold:**
   ```bash
   python scripts/extract_keyframes.py video.mp4 keyframes/ --scene-threshold 20
   ```

2. **Reduce interval:**
   ```bash
   python scripts/extract_keyframes.py video.mp4 keyframes/ --interval 5
   ```

3. **Check video file:**
   ```bash
   ffmpeg -i video.mp4  # Verify video is readable
   ```

### Too many keyframes

**Symptoms:**
- Hundreds or thousands of keyframes extracted
- Output document is huge

**Solutions:**

1. **Increase scene threshold:**
   ```bash
   python scripts/extract_keyframes.py video.mp4 keyframes/ --scene-threshold 45
   ```

2. **Increase interval:**
   ```bash
   python scripts/extract_keyframes.py video.mp4 keyframes/ --interval 20
   ```

### "Could not open video" error

**Problem:** Video file not found or corrupted.

**Solutions:**

1. **Check file exists:**
   ```bash
   ls -lh video.mp4
   ```

2. **Verify video plays:**
   ```bash
   ffplay video.mp4  # or vlc, mpv, etc.
   ```

3. **Re-download:**
   ```bash
   yt-dlp -f "best[ext=mp4]" URL
   ```

## Transcript Issues

### No transcript available

**Problem:** YouTube video doesn't have auto-generated captions.

**Solutions:**

1. **Manual transcript:** Create your own VTT file
2. **Speech-to-text:** Use tools like Whisper
3. **Skip transcript:** Process without (keyframes only)

```bash
# Process without transcript
python scripts/process_video.py video.mp4 output
```

### Transcript parsing error

**Symptoms:**
```
Error parsing transcript: invalid timestamp format
```

**Solutions:**

1. **Check VTT format:**
   ```vtt
   WEBVTT

   00:00:00.000 --> 00:00:05.000
   First subtitle text

   00:00:05.000 --> 00:00:10.000
   Second subtitle text
   ```

2. **Re-download transcript:**
   ```bash
   yt-dlp --write-auto-sub --sub-format vtt --skip-download URL
   ```

3. **Manual fix:** Edit VTT file to fix formatting

## Document Generation Issues

### "python-docx not installed"

**Solution:**

```bash
pip install python-docx
```

### Images not showing in DOCX

**Problem:** Image paths are incorrect or files moved.

**Solutions:**

1. **Verify keyframes exist:**
   ```bash
   ls -l keyframes/
   ```

2. **Use absolute paths in aligned.json**

3. **Keep keyframes directory intact until document is generated**

### Google Docs: Invalid credentials

**Symptoms:**
```
Error loading credentials: Invalid JSON
```

**Solutions:**

1. **Verify credentials file:**
   ```bash
   cat google-credentials.json | python -m json.tool
   ```

2. **Re-download credentials** from Google Cloud Console

3. **Check file path:**
   ```bash
   ls -l google-credentials.json
   ```

### Google Docs: Permission denied

**Problem:** Service account doesn't have Drive access.

**Solution:**

Follow [Google Docs setup guide](google-docs-setup.md) to:
1. Enable Google Drive API
2. Update service account scopes
3. Re-generate credentials

## VideoRAG Issues

### VideoRAG not installed

**Solution:**

See [VideoRAG installation guide](installation.md#optional-videorag-for-qa)

### CUDA out of memory

**Problem:** GPU memory insufficient for video processing.

**Solutions:**

1. **Use CPU:**
   ```bash
   export CUDA_VISIBLE_DEVICES=""
   ```

2. **Process shorter videos**

3. **Use smaller model:**
   ```bash
   python scripts/video_qa.py --working-dir ./qa --llm ollama --model llama3.1:8b
   ```

### API key errors

**Symptoms:**
```
Error: OpenAI API key required
```

**Solutions:**

```bash
# Set API key
export OPENAI_API_KEY="sk-..."

# Or use different provider
python scripts/video_qa.py --working-dir ./qa --llm ollama
```

### Slow query responses

**Solutions:**

1. **Use faster model:**
   ```bash
   --model gpt-4o-mini
   ```

2. **Disable references:**
   ```bash
   --no-references
   ```

3. **Use GPU for VideoRAG**

## Path Issues (macOS/Windows)

### Script can't find files

**Problem:** Path separators differ between platforms.

**Solution:** Use forward slashes or let the script handle paths:

```bash
# Good (works everywhere)
python scripts/process_video.py video.mp4 output

# Avoid (platform-specific)
python scripts\process_video.py video.mp4 output
```

### Permission denied

**macOS/Linux:**

```bash
chmod +x scripts/*.py
```

**Windows:**
Run Command Prompt as Administrator

## Performance Issues

### Slow keyframe extraction

**Causes:**
- Large video file (4K, high bitrate)
- Slow disk (HDD vs SSD)
- Low scene threshold (processing many frames)

**Solutions:**

1. **Increase scene threshold:**
   ```bash
   --scene-threshold 40
   ```

2. **Use SSD storage**

3. **Pre-process video:**
   ```bash
   # Reduce resolution
   ffmpeg -i input.mp4 -vf scale=1920:1080 output.mp4
   ```

### Large output files

**Problem:** HTML file is 50+ MB.

**Solutions:**

1. **Use DOCX format:**
   ```bash
   --format docx
   ```

2. **Reduce keyframes:**
   ```bash
   --scene-threshold 40 --interval 15
   ```

3. **Lower image quality:**
   ```bash
   --format jpg  # instead of png
   ```

## Common Error Messages

### "FileNotFoundError: aligned.json"

**Cause:** Alignment step failed or skipped.

**Solution:**

```bash
# Run alignment step
python scripts/align_transcript_keyframes.py transcript.vtt keyframes/keyframes_metadata.json aligned.json
```

### "JSONDecodeError"

**Cause:** Corrupted JSON file.

**Solution:**

1. **Validate JSON:**
   ```bash
   python -m json.tool aligned.json
   ```

2. **Re-generate file:**
   ```bash
   # Re-run previous step
   python scripts/align_transcript_keyframes.py ...
   ```

### "TypeError: unsupported operand type(s)"

**Cause:** Version mismatch or corrupted data.

**Solutions:**

1. **Update dependencies:**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. **Check Python version:**
   ```bash
   python --version  # Should be 3.11+
   ```

## Getting Help

If you encounter an issue not covered here:

1. **Check logs:** Look for detailed error messages
2. **Enable debug mode:**
   ```bash
   export DEBUG=1
   python scripts/process_video.py ...
   ```

3. **Minimal reproducible example:** Try with a small test video

4. **Report issue:** https://github.com/edvantageAI/agent-skills/issues

Include:
- Python version
- OS and version
- Full error message
- Steps to reproduce

## Next Steps

- [Quickstart Guide](quickstart.md) - Get started
- [Configuration Reference](configuration.md) - Customize settings
- [API Reference](api-reference.md) - Script parameters
