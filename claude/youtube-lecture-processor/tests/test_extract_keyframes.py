"""
Unit tests for keyframe extraction functionality.
"""

import unittest
import sys
from pathlib import Path
import tempfile
import shutil
import json

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from extract_keyframes import calculate_frame_difference, load_config
import numpy as np


class TestCalculateFrameDifference(unittest.TestCase):
    """Test frame difference calculation."""

    def test_identical_frames(self):
        """Identical frames should have zero difference."""
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        diff = calculate_frame_difference(frame, frame)
        self.assertEqual(diff, 0.0)

    def test_different_frames(self):
        """Different frames should have non-zero difference."""
        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2 = np.ones((100, 100, 3), dtype=np.uint8) * 255
        diff = calculate_frame_difference(frame1, frame2)
        self.assertGreater(diff, 0.0)

    def test_none_frames(self):
        """None frames should return infinity."""
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        diff1 = calculate_frame_difference(None, frame)
        diff2 = calculate_frame_difference(frame, None)
        diff3 = calculate_frame_difference(None, None)
        self.assertEqual(diff1, float('inf'))
        self.assertEqual(diff2, float('inf'))
        self.assertEqual(diff3, float('inf'))


class TestLoadConfig(unittest.TestCase):
    """Test configuration loading."""

    def test_load_nonexistent_config(self):
        """Loading non-existent config should return empty dict."""
        config = load_config('/nonexistent/config.yaml')
        self.assertEqual(config, {})

    def test_load_valid_config(self):
        """Loading valid config should return dict with settings."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
keyframe_extraction:
  scene_threshold: 25.0
  interval_seconds: 15
            """)
            temp_config = f.name

        try:
            config = load_config(temp_config)
            self.assertIn('keyframe_extraction', config)
            self.assertEqual(config['keyframe_extraction']['scene_threshold'], 25.0)
        finally:
            Path(temp_config).unlink()


if __name__ == '__main__':
    unittest.main()
