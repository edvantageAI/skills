"""
Custom exceptions for YouTube Lecture Processor.
"""


class YLPError(Exception):
    """Base exception for YouTube Lecture Processor."""
    pass


class VideoNotFoundError(YLPError):
    """Video file not found."""
    pass


class TranscriptParseError(YLPError):
    """Failed to parse transcript."""
    pass


class KeyframeExtractionError(YLPError):
    """Failed to extract keyframes."""
    pass


class AlignmentError(YLPError):
    """Failed to align transcript with keyframes."""
    pass


class DocumentGenerationError(YLPError):
    """Failed to generate document."""
    pass


class ConfigurationError(YLPError):
    """Configuration error."""
    pass


class VideoRAGError(YLPError):
    """VideoRAG operation failed."""
    pass
