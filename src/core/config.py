"""Core configuration and environment settings."""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Keys
    deepgram_api_key: str = ""
    groq_api_key: str = ""
    
    # Paths
    audio_dir: Path = Path("audio/raw")
    transcript_dir: Path = Path("transcripts")
    dataset_dir: Path = Path("dataset")
    
    # Audio Processing
    audio_sample_rate: int = 16000
    audio_channels: int = 1
    audio_bitrate: str = "192"
    
    # Transcription
    transcription_model: str = "nova-3"
    transcription_language: str = "ur"
    
    # Dataset Filtering
    min_segment_duration: float = 1.0
    max_segment_duration: float = 12.0
    
    # LLM
    llm_model: str = "llama-3.3-70b-versatile"
    llm_temperature: float = 0.0
    
    # Retry Configuration
    max_retries: int = 3
    retry_delay: float = 1.0
    
    model_config = {"env_file": ".env", "case_sensitive": False}


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    settings = Settings()
    
    # Ensure directories exist
    for directory in [settings.audio_dir, settings.transcript_dir, settings.dataset_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    
    return settings
