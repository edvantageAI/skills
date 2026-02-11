"""
Unit tests for document creation functionality.
"""

import unittest
import sys
from pathlib import Path
import tempfile
import json

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from create_document import load_config


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
document_generation:
  default_format: docx
  docx:
    image_width_inches: 4.0
            """)
            temp_config = f.name

        try:
            config = load_config(temp_config)
            self.assertIn('document_generation', config)
            self.assertEqual(config['document_generation']['default_format'], 'docx')
            self.assertEqual(config['document_generation']['docx']['image_width_inches'], 4.0)
        finally:
            Path(temp_config).unlink()


class TestDocumentGeneration(unittest.TestCase):
    """Test document generation functions."""

    def setUp(self):
        """Set up test data."""
        self.aligned_data = {
            'video_info': {
                'video_path': 'test.mp4',
                'duration': 100.0,
                'fps': 30.0
            },
            'aligned_items': [
                {
                    'keyframe': {
                        'index': 0,
                        'timestamp': 0.0,
                        'filepath': 'keyframe_0.jpg'
                    },
                    'transcript': 'Test transcript'
                }
            ]
        }

    def test_aligned_data_structure(self):
        """Test that aligned data has correct structure."""
        self.assertIn('video_info', self.aligned_data)
        self.assertIn('aligned_items', self.aligned_data)
        self.assertEqual(len(self.aligned_data['aligned_items']), 1)

        item = self.aligned_data['aligned_items'][0]
        self.assertIn('keyframe', item)
        self.assertIn('transcript', item)


if __name__ == '__main__':
    unittest.main()
