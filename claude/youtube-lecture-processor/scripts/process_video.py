#!/usr/bin/env python3
"""
Unified workflow script for YouTube Lecture Processor.
Automates the full pipeline: download → transcript → keyframes → align → document.
"""

import argparse
import sys
import os
from pathlib import Path
import subprocess
import yaml
import logging
import shutil
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path=None):
    """Load configuration from YAML file."""
    if config_path is None:
        config_path = Path(__file__).parent.parent / 'config.yaml'

    config_path = Path(config_path)
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Failed to load config from {config_path}: {e}")
            return {}
    return {}


def is_youtube_url(input_str):
    """Check if input is a YouTube URL."""
    return 'youtube.com' in input_str or 'youtu.be' in input_str


def download_video(url, output_dir):
    """
    Download YouTube video using yt-dlp.

    Returns:
        tuple: (video_path, transcript_path) or (video_path, None)
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Downloading video from: {url}")

    # Download video
    video_output = output_dir / "video.mp4"
    cmd = [
        'yt-dlp',
        '-f', 'best[ext=mp4]',
        '-o', str(video_output),
        url
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info("Video downloaded successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to download video: {e.stderr}")
        raise

    # Try to download transcript
    transcript_output = output_dir / "transcript.vtt"
    cmd_transcript = [
        'yt-dlp',
        '--write-auto-sub',
        '--sub-format', 'vtt',
        '--skip-download',
        '-o', str(output_dir / "transcript"),
        url
    ]

    try:
        subprocess.run(cmd_transcript, check=True, capture_output=True, text=True)
        # Find the generated transcript file
        transcript_files = list(output_dir.glob("transcript*.vtt"))
        if transcript_files:
            transcript_path = transcript_files[0]
            logger.info(f"Transcript downloaded: {transcript_path}")
            return video_output, transcript_path
        else:
            logger.warning("No transcript available for this video")
            return video_output, None
    except subprocess.CalledProcessError:
        logger.warning("Could not download transcript")
        return video_output, None


def extract_keyframes_step(video_path, output_dir, scene_threshold, interval, output_format):
    """Extract keyframes from video."""
    logger.info("Extracting keyframes...")

    script_dir = Path(__file__).parent
    cmd = [
        sys.executable,
        str(script_dir / 'extract_keyframes.py'),
        str(video_path),
        str(output_dir),
        '--scene-threshold', str(scene_threshold),
        '--interval', str(interval),
        '--format', output_format
    ]

    try:
        subprocess.run(cmd, check=True)
        metadata_path = output_dir / 'keyframes_metadata.json'
        return metadata_path
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to extract keyframes: {e}")
        raise


def align_transcript_step(transcript_path, keyframes_metadata, output_path):
    """Align transcript with keyframes."""
    logger.info("Aligning transcript with keyframes...")

    script_dir = Path(__file__).parent
    cmd = [
        sys.executable,
        str(script_dir / 'align_transcript_keyframes.py'),
        str(transcript_path),
        str(keyframes_metadata),
        str(output_path)
    ]

    try:
        subprocess.run(cmd, check=True)
        return output_path
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to align transcript: {e}")
        raise


def create_document_step(aligned_json, output_path, doc_format, credentials, image_width):
    """Create final document."""
    logger.info(f"Creating {doc_format.upper()} document...")

    script_dir = Path(__file__).parent
    cmd = [
        sys.executable,
        str(script_dir / 'create_document.py'),
        str(aligned_json),
        str(output_path),
        '--format', doc_format,
        '--image-width', str(image_width)
    ]

    if doc_format == 'gdoc' and credentials:
        cmd.extend(['--credentials', str(credentials)])

    try:
        subprocess.run(cmd, check=True)
        return output_path
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to create document: {e}")
        raise


def cleanup_intermediate_files(working_dir, keep_video=False):
    """Clean up intermediate files."""
    logger.info("Cleaning up intermediate files...")

    working_dir = Path(working_dir)

    # Remove keyframes directory
    keyframes_dir = working_dir / 'keyframes'
    if keyframes_dir.exists():
        shutil.rmtree(keyframes_dir)
        logger.info(f"Removed: {keyframes_dir}")

    # Remove aligned JSON
    aligned_json = working_dir / 'aligned.json'
    if aligned_json.exists():
        aligned_json.unlink()
        logger.info(f"Removed: {aligned_json}")

    # Remove video if requested
    if not keep_video:
        video_file = working_dir / 'video.mp4'
        if video_file.exists():
            video_file.unlink()
            logger.info(f"Removed: {video_file}")

    # Remove transcript
    transcript_files = list(working_dir.glob('transcript*.vtt'))
    for tf in transcript_files:
        tf.unlink()
        logger.info(f"Removed: {tf}")


def main():
    # Load configuration
    config = load_config()
    keyframe_config = config.get('keyframe_extraction', {})
    doc_config = config.get('document_generation', {})
    path_config = config.get('paths', {})

    # Set defaults from config
    default_scene_threshold = keyframe_config.get('scene_threshold', 30.0)
    default_interval = keyframe_config.get('interval_seconds', 10)
    default_format = keyframe_config.get('output_format', 'jpg')
    default_doc_format = doc_config.get('default_format', 'html')
    default_image_width = doc_config.get('docx', {}).get('image_width_inches', 3.0)
    default_working_dir = path_config.get('working_dir', './working')
    default_output_dir = path_config.get('output_dir', './output')

    parser = argparse.ArgumentParser(
        description='Process YouTube videos into study notes',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process YouTube URL to HTML
  python process_video.py "https://youtube.com/watch?v=..." output_notes

  # Process local MP4 to DOCX
  python process_video.py lecture.mp4 lecture_notes --format docx

  # Custom settings
  python process_video.py video.mp4 output --scene-threshold 40 --interval 15

  # Keep intermediate files for inspection
  python process_video.py video.mp4 output --keep-intermediate

  # Create Google Doc
  python process_video.py "https://youtube.com/watch?v=..." notes --format gdoc --credentials credentials.json
        """
    )

    parser.add_argument('input', help='YouTube URL or local video file')
    parser.add_argument('output_name', help='Output name (without extension)')
    parser.add_argument('--format', choices=['html', 'docx', 'gdoc'],
                        default=default_doc_format, help=f'Output format (default: {default_doc_format})')
    parser.add_argument('--working-dir', default=default_working_dir,
                        help=f'Working directory for intermediate files (default: {default_working_dir})')
    parser.add_argument('--output-dir', default=default_output_dir,
                        help=f'Output directory for final document (default: {default_output_dir})')
    parser.add_argument('--scene-threshold', type=float, default=default_scene_threshold,
                        help=f'Scene change threshold (default: {default_scene_threshold})')
    parser.add_argument('--interval', type=int, default=default_interval,
                        help=f'Keyframe interval in seconds (default: {default_interval})')
    parser.add_argument('--keyframe-format', choices=['jpg', 'png'], default=default_format,
                        help=f'Keyframe image format (default: {default_format})')
    parser.add_argument('--image-width', type=float, default=default_image_width,
                        help=f'Image width in inches for DOCX/GDoc (default: {default_image_width})')
    parser.add_argument('--keep-intermediate', action='store_true',
                        help='Keep intermediate files (video, keyframes, etc.)')
    parser.add_argument('--credentials', help='Google API credentials (for gdoc format)')
    parser.add_argument('--config', help='Config file path')

    args = parser.parse_args()

    # Reload config if custom path provided
    if args.config:
        config = load_config(args.config)

    # Validate gdoc format requires credentials
    if args.format == 'gdoc' and not args.credentials:
        logger.error("Google Docs format requires --credentials argument")
        sys.exit(1)

    # Setup directories
    working_dir = Path(args.working_dir)
    output_dir = Path(args.output_dir)
    working_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Step 1: Get video file
        if is_youtube_url(args.input):
            video_path, transcript_path = download_video(args.input, working_dir)
        else:
            video_path = Path(args.input)
            if not video_path.exists():
                logger.error(f"Video file not found: {video_path}")
                sys.exit(1)
            transcript_path = None
            logger.info(f"Using local video: {video_path}")

        # Step 2: Extract keyframes
        keyframes_dir = working_dir / 'keyframes'
        keyframes_metadata = extract_keyframes_step(
            video_path,
            keyframes_dir,
            args.scene_threshold,
            args.interval,
            args.keyframe_format
        )

        # Step 3: Align transcript (if available)
        if transcript_path and transcript_path.exists():
            aligned_json = working_dir / 'aligned.json'
            align_transcript_step(transcript_path, keyframes_metadata, aligned_json)
        else:
            logger.warning("No transcript available, creating minimal aligned data")
            # Create minimal aligned data with keyframes only
            with open(keyframes_metadata, 'r') as f:
                metadata = json.load(f)

            aligned_data = {
                'video_info': {
                    'video_path': str(video_path),
                    'duration': metadata.get('duration', 0),
                    'fps': metadata.get('fps', 0)
                },
                'aligned_items': [
                    {
                        'keyframe': kf,
                        'transcript': ''
                    }
                    for kf in metadata.get('keyframes', [])
                ]
            }

            aligned_json = working_dir / 'aligned.json'
            with open(aligned_json, 'w') as f:
                json.dump(aligned_data, f, indent=2)

        # Step 4: Create document
        if args.format == 'html':
            output_path = output_dir / f"{args.output_name}.html"
        elif args.format == 'docx':
            output_path = output_dir / f"{args.output_name}.docx"
        else:  # gdoc
            output_path = output_dir / f"{args.output_name}_gdoc.json"

        create_document_step(
            aligned_json,
            output_path,
            args.format,
            args.credentials,
            args.image_width
        )

        # Step 5: Cleanup (unless --keep-intermediate)
        if not args.keep_intermediate:
            cleanup_intermediate_files(working_dir, keep_video=False)

        logger.info("=" * 60)
        logger.info("✅ Processing complete!")
        logger.info(f"Output: {output_path}")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Processing failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
