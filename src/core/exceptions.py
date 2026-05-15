"""Custom exception classes for error handling."""


class PipelineError(Exception):
    """Base exception for pipeline errors."""
    pass


class DownloadError(PipelineError):
    """Raised when YouTube download fails."""
    pass


class DownloadTimeout(DownloadError):
    """Raised when download exceeds timeout."""
    pass


class TranscriptionError(PipelineError):
    """Raised when transcription fails."""
    pass


class DatasetBuildError(PipelineError):
    """Raised when dataset building fails."""
    pass


class ValidationError(PipelineError):
    """Raised when data validation fails."""
    pass


class AudioProcessingError(PipelineError):
    """Raised when audio processing fails."""
    pass
