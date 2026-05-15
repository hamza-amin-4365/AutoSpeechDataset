"""Pydantic models for data validation."""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from pathlib import Path


class VideoMetadata(BaseModel):
    """YouTube video metadata."""
    video_id: str
    title: Optional[str] = None
    uploader: Optional[str] = None
    url: str


class AudioFile(BaseModel):
    """Audio file information."""
    video_id: str
    path: Path
    sample_rate: int = 16000
    channels: int = 1
    
    @field_validator('path')
    @classmethod
    def validate_path_exists(cls, v: Path) -> Path:
        if not v.exists():
            raise ValueError(f"Audio file does not exist: {v}")
        return v


class TranscriptSegment(BaseModel):
    """Single transcript segment."""
    start: float = Field(..., ge=0)
    end: float = Field(..., gt=0)
    text: str = Field(..., min_length=1)
    
    @field_validator('end')
    @classmethod
    def validate_end_after_start(cls, v: float, info) -> float:
        if 'start' in info.data and v <= info.data['start']:
            raise ValueError("end must be greater than start")
        return v
    
    @property
    def duration(self) -> float:
        return self.end - self.start


class Transcript(BaseModel):
    """Complete transcript with segments."""
    video_id: str
    path: Path
    segments: list[TranscriptSegment]
    language: str = "ur"


class DatasetEntry(BaseModel):
    """Single dataset entry."""
    id: str
    audio_path: Path
    start: float = Field(..., ge=0)
    end: float = Field(..., gt=0)
    text: str = Field(..., min_length=1)
    duration: float = Field(..., gt=0)
    
    @field_validator('duration')
    @classmethod
    def validate_duration_range(cls, v: float) -> float:
        if not (1.0 <= v <= 12.0):
            raise ValueError(f"Duration {v}s outside valid range [1.0, 12.0]")
        return v


class Dataset(BaseModel):
    """Complete dataset."""
    video_id: str
    path: Path
    entries: list[DatasetEntry]
    total_duration: float = 0.0
    
    @property
    def count(self) -> int:
        return len(self.entries)


class PipelineRequest(BaseModel):
    """Pipeline execution request."""
    youtube_url: str = Field(..., pattern=r'(youtube\.com|youtu\.be)')
    thread_id: Optional[str] = None


class PipelineResult(BaseModel):
    """Pipeline execution result."""
    video_id: str
    audio_path: Optional[Path] = None
    transcript_path: Optional[Path] = None
    dataset_path: Optional[Path] = None
    status: str = "success"
    error: Optional[str] = None
    messages: list[str] = Field(default_factory=list)
