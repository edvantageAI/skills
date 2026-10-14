#!/usr/bin/env python3
"""
Extract keyframes from video using scene detection and time-based fallback.
Optimized for lecture videos with slides and application demonstrations.
"""

import cv2
import argparse
import os
import sys
from pathlib import Path
import json
import yaml
import logging

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


def calculate_frame_difference(frame1, frame2):
    """Calculate the difference between two frames."""
    if frame1 is None or frame2 is None:
        return float('inf')
    
    # Convert to grayscale for comparison
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    
    # Calculate absolute difference
    diff = cv2.absdiff(gray1, gray2)
    
    # Return mean difference
    return diff.mean()


def extract_keyframes(video_path, output_dir, scene_threshold=30.0, interval_seconds=10, output_format='jpg'):
    """
    Extract keyframes using combined scene detection and interval-based approach.

    Args:
        video_path: Path to input video file
        output_dir: Directory to save keyframes
        scene_threshold: Threshold for scene change detection (0-255, higher = more sensitive)
        interval_seconds: Fallback interval in seconds for extracting frames
        output_format: Output image format (jpg or png)

    Returns:
        List of dictionaries with keyframe info (timestamp, frame_number, filepath)
    """
    # Convert to Path objects for cross-platform compatibility
    video_path = Path(video_path)
    output_dir = Path(output_dir)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Open video
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")

    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps

    logger.info(f"Video: {video_path}")
    logger.info(f"FPS: {fps}, Total frames: {total_frames}, Duration: {duration:.2f}s")
    
    keyframes = []
    prev_frame = None
    frame_count = 0
    last_keyframe_time = -interval_seconds  # Force first frame to be captured
    
    interval_frames = int(fps * interval_seconds)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        timestamp = frame_count / fps
        
        # Check if we should extract this frame
        should_extract = False
        reason = ""
        
        # Scene change detection
        if prev_frame is not None:
            diff = calculate_frame_difference(prev_frame, frame)
            if diff > scene_threshold:
                should_extract = True
                reason = "scene_change"
        
        # Interval-based fallback
        if not should_extract and (timestamp - last_keyframe_time) >= interval_seconds:
            should_extract = True
            reason = "interval"
        
        # First frame
        if frame_count == 0:
            should_extract = True
            reason = "first_frame"
        
        # Extract keyframe
        if should_extract:
            filename = f"keyframe_{len(keyframes):04d}_t{timestamp:.2f}s.{output_format}"
            filepath = output_dir / filename
            cv2.imwrite(str(filepath), frame)

            keyframes.append({
                'index': len(keyframes),
                'frame_number': frame_count,
                'timestamp': round(timestamp, 2),
                'filepath': str(filepath),
                'reason': reason
            })

            last_keyframe_time = timestamp
            logger.info(f"Extracted keyframe {len(keyframes)}: {filename} ({reason})")
        
        prev_frame = frame.copy()
        frame_count += 1
    
    cap.release()

    logger.info(f"Total keyframes extracted: {len(keyframes)}")

    # Save metadata
    metadata_path = output_dir / "keyframes_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump({
            'video_path': str(video_path),
            'fps': fps,
            'total_frames': total_frames,
            'duration': duration,
            'scene_threshold': scene_threshold,
            'interval_seconds': interval_seconds,
            'output_format': output_format,
            'keyframes': keyframes
        }, f, indent=2)

    logger.info(f"Metadata saved to: {metadata_path}")
    
    return keyframes


def main():
    # Load configuration
    config = load_config()
    keyframe_config = config.get('keyframe_extraction', {})

    # Set defaults from config
    default_scene_threshold = keyframe_config.get('scene_threshold', 30.0)
    default_interval = keyframe_config.get('interval_seconds', 10)
    default_format = keyframe_config.get('output_format', 'jpg')

    parser = argparse.ArgumentParser(description='Extract keyframes from video')
    parser.add_argument('video_path', help='Path to input video file')
    parser.add_argument('output_dir', help='Directory to save keyframes')
    parser.add_argument('--scene-threshold', type=float, default=default_scene_threshold,
                        help=f'Scene change threshold (default: {default_scene_threshold})')
    parser.add_argument('--interval', type=int, default=default_interval,
                        help=f'Fallback interval in seconds (default: {default_interval})')
    parser.add_argument('--format', choices=['jpg', 'png'], default=default_format,
                        help=f'Output image format (default: {default_format})')
    parser.add_argument('--config', help='Path to config file')

    args = parser.parse_args()

    # Reload config if custom path provided
    if args.config:
        config = load_config(args.config)
        keyframe_config = config.get('keyframe_extraction', {})

    if not Path(args.video_path).exists():
        logger.error(f"Video file not found: {args.video_path}")
        sys.exit(1)

    try:
        keyframes = extract_keyframes(
            args.video_path,
            args.output_dir,
            scene_threshold=args.scene_threshold,
            interval_seconds=args.interval,
            output_format=args.format
        )
        logger.info(f"✅ Successfully extracted {len(keyframes)} keyframes")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
