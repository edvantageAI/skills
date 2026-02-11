# Tests

Unit tests for YouTube Lecture Processor.

## Running Tests

### Run All Tests

```bash
python -m pytest tests/
```

Or using unittest:

```bash
python -m unittest discover tests/
```

### Run Specific Test File

```bash
python -m pytest tests/test_extract_keyframes.py
```

### Run with Coverage

```bash
pip install pytest-cov
python -m pytest tests/ --cov=scripts --cov-report=html
```

View coverage report:

```bash
open htmlcov/index.html
```

## Test Structure

```
tests/
├── test_extract_keyframes.py    # Keyframe extraction tests
├── test_align_transcript.py     # Transcript alignment tests
├── test_create_document.py      # Document generation tests
└── README.md                    # This file
```

## Writing Tests

### Test Template

```python
import unittest
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from your_module import your_function


class TestYourFunction(unittest.TestCase):
    """Test description."""

    def test_basic_case(self):
        """Test basic functionality."""
        result = your_function(input_data)
        self.assertEqual(result, expected_output)


if __name__ == '__main__':
    unittest.main()
```

### Best Practices

- One test file per script
- Use descriptive test names
- Test edge cases (empty input, None, etc.)
- Use setUp() for common test data
- Clean up temp files in tearDown()

## Current Test Coverage

- ✅ Keyframe extraction (frame difference, config loading)
- ✅ Transcript alignment (timestamp parsing, alignment logic)
- ✅ Document generation (config loading, data structure)
- ⚠️ Integration tests (TODO)
- ⚠️ End-to-end tests (TODO)

## Future Tests

### Integration Tests
- Full pipeline test (video → document)
- Cross-format compatibility
- Error handling and recovery

### Performance Tests
- Large video processing
- Memory usage profiling
- Concurrent processing

### Compatibility Tests
- Different video formats
- Various transcript formats
- Platform-specific paths

## Continuous Integration

### GitHub Actions (TODO)

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements-dev.txt
      - name: Run tests
        run: python -m pytest tests/
```

## Debugging Tests

### Verbose Output

```bash
python -m pytest tests/ -v
```

### Print Statements

```bash
python -m pytest tests/ -s
```

### Run Single Test

```bash
python -m pytest tests/test_extract_keyframes.py::TestCalculateFrameDifference::test_identical_frames
```

## Next Steps

- Add more edge case tests
- Implement integration tests
- Set up CI/CD pipeline
- Add performance benchmarks
