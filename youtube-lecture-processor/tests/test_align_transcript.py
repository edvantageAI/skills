"""
Unit tests for transcript alignment functionality.
"""

import unittest
import sys
from pathlib import Path
import tempfile

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from align_transcript_keyframes import parse_timestamp, align_transcript_to_keyframes


class TestParseTimestamp(unittest.TestCase):
    """Test timestamp parsing."""

    def test_hms_format(self):
        """Test HH:MM:SS.mmm format."""
        self.assertEqual(parse_timestamp('01:23:45.678'), 5025.678)
        self.assertEqual(parse_timestamp('00:00:00.000'), 0.0)

    def test_ms_format(self):
        """Test MM:SS.mmm format."""
        self.assertEqual(parse_timestamp('12:34.567'), 754.567)
        self.assertEqual(parse_timestamp('00:00.000'), 0.0)

    def test_seconds_only(self):
        """Test seconds only format."""
        self.assertEqual(parse_timestamp('123.456'), 123.456)
        self.assertEqual(parse_timestamp('0'), 0.0)


class TestAlignTranscriptToKeyframes(unittest.TestCase):
    """Test transcript-keyframe alignment."""

    def test_exact_alignment(self):
        """Test alignment with exact timestamp matches."""
        transcript_segments = [
            {'start': 0.0, 'end': 5.0, 'text': 'First segment'},
            {'start': 5.0, 'end': 10.0, 'text': 'Second segment'},
            {'start': 10.0, 'end': 15.0, 'text': 'Third segment'}
        ]

        keyframes = [
            {'timestamp': 0.0, 'index': 0, 'filepath': 'frame0.jpg'},
            {'timestamp': 5.0, 'index': 1, 'filepath': 'frame1.jpg'},
            {'timestamp': 10.0, 'index': 2, 'filepath': 'frame2.jpg'}
        ]

        aligned = align_transcript_to_keyframes(transcript_segments, keyframes)

        self.assertEqual(len(aligned), 3)
        self.assertEqual(aligned[0]['transcript'], 'First segment')
        self.assertEqual(aligned[1]['transcript'], 'Second segment')
        self.assertEqual(aligned[2]['transcript'], 'Third segment')

    def test_approximate_alignment(self):
        """Test alignment with approximate timestamp matches."""
        transcript_segments = [
            {'start': 0.0, 'end': 10.0, 'text': 'First segment'},
        ]

        keyframes = [
            {'timestamp': 3.5, 'index': 0, 'filepath': 'frame0.jpg'},
        ]

        aligned = align_transcript_to_keyframes(transcript_segments, keyframes)

        self.assertEqual(len(aligned), 1)
        self.assertEqual(aligned[0]['transcript'], 'First segment')

    def test_empty_transcript(self):
        """Test alignment with no transcript segments."""
        transcript_segments = []

        keyframes = [
            {'timestamp': 0.0, 'index': 0, 'filepath': 'frame0.jpg'},
        ]

        aligned = align_transcript_to_keyframes(transcript_segments, keyframes)

        self.assertEqual(len(aligned), 1)
        self.assertEqual(aligned[0]['transcript'], '')


if __name__ == '__main__':
    unittest.main()
