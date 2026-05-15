"""YouTube download and metadata extraction service."""
import asyncio
from pathlib import Path
from typing import Optional
from yt_dlp import YoutubeDL

from src.core.config import get_settings
from src.core.exceptions import DownloadError, DownloadTimeout
from src.core.logging import get_logger
from src.schemas.models import VideoMetadata, AudioFile
from src.utils.url_helpers import extract_video_id

logger = get_logger("youtube_service")
settings = get_settings()


class YouTubeService:
    """Handles YouTube video downloads and metadata extraction."""
    
    def __init__(self):
        self.settings = settings
        self.audio_dir = settings.audio_dir
        
    async def get_metadata(self, url: str) -> VideoMetadata:
        """Fetch video metadata without downloading.
        
        Args:
            url: YouTube video URL
            
        Returns:
            VideoMetadata object
            
        Raises:
            DownloadError: If metadata extraction fails
        """
        try:
            video_id = extract_video_id(url)
            
            ydl_opts = {
                "quiet": True,
                "skip_download": True,
                "no_warnings": True,
            }
            
            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(
                None,
                lambda: self._extract_info(url, ydl_opts)
            )
            
            metadata = VideoMetadata(
                video_id=video_id,
                title=info.get("title"),
                uploader=info.get("uploader"),
                url=url
            )
            
            logger.info(f"Fetched metadata for video: {video_id}")
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to fetch metadata: {e}")
            raise DownloadError(f"Metadata extraction failed: {e}")
    
    async def download_audio(
        self,
        url: str,
        video_id: Optional[str] = None,
        force: bool = False
    ) -> AudioFile:
        """Download audio from YouTube video.
        
        Args:
            url: YouTube video URL
            video_id: Optional pre-extracted video ID
            force: Force re-download even if cached
            
        Returns:
            AudioFile object with path and metadata
            
        Raises:
            DownloadError: If download fails
            DownloadTimeout: If download exceeds timeout
        """
        try:
            if not video_id:
                video_id = extract_video_id(url)
            
            audio_path = self.audio_dir / f"{video_id}.wav"
            
            # Check cache
            if audio_path.exists() and not force:
                logger.info(f"Using cached audio: {audio_path}")
                return AudioFile(
                    video_id=video_id,
                    path=audio_path,
                    sample_rate=settings.audio_sample_rate,
                    channels=settings.audio_channels
                )
            
            # Download with retries
            for attempt in range(settings.max_retries):
                try:
                    await self._download_with_ytdlp(url, video_id)
                    break
                except Exception as e:
                    if attempt == settings.max_retries - 1:
                        raise
                    logger.warning(f"Download attempt {attempt + 1} failed: {e}")
                    await asyncio.sleep(settings.retry_delay * (attempt + 1))
            
            if not audio_path.exists():
                raise DownloadError(f"Audio file not created: {audio_path}")
            
            logger.info(f"Downloaded audio: {audio_path}")
            return AudioFile(
                video_id=video_id,
                path=audio_path,
                sample_rate=settings.audio_sample_rate,
                channels=settings.audio_channels
            )
            
        except Exception as e:
            logger.error(f"Audio download failed: {e}")
            raise DownloadError(f"Failed to download audio: {e}")
    
    def _extract_info(self, url: str, opts: dict) -> dict:
        """Synchronous info extraction (runs in executor)."""
        with YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=False)
    
    async def _download_with_ytdlp(self, url: str, video_id: str) -> None:
        """Execute yt-dlp download in executor."""
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": str(self.audio_dir / "%(id)s.%(ext)s"),
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": settings.audio_bitrate,
            }],
            "postprocessor_args": [
                "-ac", str(settings.audio_channels),
                "-ar", str(settings.audio_sample_rate)
            ],
            "quiet": False,
            "no_warnings": True,
        }
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self._download_sync(url, ydl_opts)
        )
    
    def _download_sync(self, url: str, opts: dict) -> None:
        """Synchronous download (runs in executor)."""
        with YoutubeDL(opts) as ydl:
            ydl.download([url])
