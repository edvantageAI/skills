#!/usr/bin/env python3
"""
Align transcript segments with keyframe screenshots for 1:1 mapping.
"""

import json
import argparse
import sys
from pathlib import Path
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


def parse_transcript_with_timestamps(transcript_file):
    """
    Parse transcript file and extract segments with timestamps.
    Supports various formats (VTT, SRT, or plain text with timestamps).

    Returns list of segments: [{'start': seconds, 'end': seconds, 'text': str}, ...]
    """
    transcript_file = Path(transcript_file)
    if not transcript_file.exists():
        raise FileNotFoundError(f"Transcript file not found: {transcript_file}")

    with open(transcript_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    segments = []
    
    # Check if it's VTT format
    if 'WEBVTT' in content or '-->' in content:
        lines = content.split('\n')
        current_segment = {'start': 0, 'end': 0, 'text': ''}
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and metadata
            if not line or line.startswith('WEBVTT') or line.isdigit():
                continue
            
            # Parse timestamp line
            if '-->' in line:
                parts = line.split('-->')
                start_time = parse_timestamp(parts[0].strip())
                end_time = parse_timestamp(parts[1].strip().split()[0])  # Remove any trailing info
                
                if current_segment['text']:
                    segments.append(current_segment)
                
                current_segment = {'start': start_time, 'end': end_time, 'text': ''}
            else:
                # Text line
                if current_segment['text']:
                    current_segment['text'] += ' ' + line
                else:
                    current_segment['text'] = line
        
        # Add last segment
        if current_segment['text']:
            segments.append(current_segment)
    
    else:
        # Plain text - create single segment
        segments.append({
            'start': 0,
            'end': float('inf'),
            'text': content.strip()
        })
    
    return segments


def parse_timestamp(timestamp_str):
    """Convert timestamp string (HH:MM:SS.mmm or MM:SS.mmm) to seconds."""
    parts = timestamp_str.strip().split(':')
    
    if len(parts) == 3:  # HH:MM:SS.mmm
        hours, minutes, seconds = parts
        return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    elif len(parts) == 2:  # MM:SS.mmm
        minutes, seconds = parts
        return int(minutes) * 60 + float(seconds)
    else:
        return float(parts[0])


def align_transcript_to_keyframes(transcript_segments, keyframes):
    """
    Align transcript segments to keyframes for 1:1 mapping.
    Each keyframe gets the transcript text that corresponds to its timestamp.
    
    Returns list of aligned items: [{'keyframe': {...}, 'transcript': str}, ...]
    """
    aligned = []
    
    for keyframe in keyframes:
        timestamp = keyframe['timestamp']
        
        # Find the transcript segment that contains this timestamp
        matching_text = ""
        
        for segment in transcript_segments:
            if segment['start'] <= timestamp <= segment['end']:
                matching_text = segment['text']
                break
        
        # If no exact match, find the closest segment
        if not matching_text and transcript_segments:
            closest_segment = min(
                transcript_segments,
                key=lambda s: min(abs(s['start'] - timestamp), abs(s['end'] - timestamp))
            )
            matching_text = closest_segment['text']
        
        aligned.append({
            'keyframe': keyframe,
            'transcript': matching_text.strip()
        })
    
    return aligned


def main():
    # Load configuration
    config = load_config()

    parser = argparse.ArgumentParser(description='Align transcript with keyframes')
    parser.add_argument('transcript_file', help='Path to transcript file (VTT, SRT, or plain text)')
    parser.add_argument('keyframes_metadata', help='Path to keyframes metadata JSON file')
    parser.add_argument('output_file', help='Path to output aligned JSON file')
    parser.add_argument('--config', help='Path to config file')

    args = parser.parse_args()

    # Reload config if custom path provided
    if args.config:
        config = load_config(args.config)

    # Convert to Path objects
    transcript_file = Path(args.transcript_file)
    keyframes_metadata = Path(args.keyframes_metadata)
    output_file = Path(args.output_file)

    # Load keyframes metadata
    try:
        if not keyframes_metadata.exists():
            raise FileNotFoundError(f"Keyframes metadata file not found: {keyframes_metadata}")

        with open(keyframes_metadata, 'r') as f:
            metadata = json.load(f)
            keyframes = metadata.get('keyframes', [])

        if not keyframes:
            raise ValueError("No keyframes found in metadata file")

        logger.info(f"Loaded {len(keyframes)} keyframes from metadata")
    except Exception as e:
        logger.error(f"Error loading keyframes metadata: {e}", exc_info=True)
        sys.exit(1)

    # Parse transcript
    try:
        transcript_segments = parse_transcript_with_timestamps(transcript_file)
        logger.info(f"Parsed {len(transcript_segments)} transcript segments")
    except Exception as e:
        logger.error(f"Error parsing transcript: {e}", exc_info=True)
        sys.exit(1)

    # Align
    try:
        aligned = align_transcript_to_keyframes(transcript_segments, keyframes)
        logger.info(f"Aligned {len(aligned)} keyframes with transcript")
    except Exception as e:
        logger.error(f"Error during alignment: {e}", exc_info=True)
        sys.exit(1)

    # Save output
    try:
        output_data = {
            'video_info': {
                'video_path': metadata.get('video_path', ''),
                'duration': metadata.get('duration', 0),
                'fps': metadata.get('fps', 0)
            },
            'aligned_items': aligned
        }

        # Create output directory if needed
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)

        logger.info(f"✅ Successfully aligned {len(aligned)} keyframes with transcript")
        logger.info(f"Output saved to: {output_file}")
    except Exception as e:
        logger.error(f"Error saving output: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
