"""Main pipeline orchestrator for sequential service execution."""
from typing import Optional

from src.core.logging import get_logger
from src.core.exceptions import PipelineError
from src.schemas.models import PipelineRequest, PipelineResult
from src.services.youtube_service import YouTubeService
from src.services.transcription_service import TranscriptionService
from src.services.processing_service import ProcessingService

logger = get_logger("pipeline_orchestrator")


class PipelineOrchestrator:
    """Orchestrates the complete pipeline execution."""
    
    def __init__(self):
        self.youtube_service = YouTubeService()
        self.transcription_service = TranscriptionService()
        self.processing_service = ProcessingService()
    
    async def execute(self, request: PipelineRequest) -> PipelineResult:
        """Execute the complete pipeline.
        
        Args:
            request: Pipeline request with YouTube URL
            
        Returns:
            PipelineResult with paths and status
        """
        messages = []
        
        try:
            logger.info(f"Starting pipeline for URL: {request.youtube_url}")
            
            # Step 1: Fetch metadata
            metadata = await self.youtube_service.get_metadata(request.youtube_url)
            messages.append(f"Fetched metadata for video: {metadata.video_id}")
            logger.info(f"Video: {metadata.title} by {metadata.uploader}")
            
            # Step 2: Download audio
            audio_file = await self.youtube_service.download_audio(
                request.youtube_url,
                video_id=metadata.video_id
            )
            messages.append(f"Downloaded audio: {audio_file.path}")
            
            # Step 3: Transcribe audio
            transcript = await self.transcription_service.transcribe(audio_file)
            messages.append(
                f"Transcribed audio: {len(transcript.segments)} segments"
            )
            
            # Step 4: Build dataset
            dataset = await self.processing_service.build_dataset(
                transcript,
                audio_file
            )
            messages.append(
                f"Built dataset: {dataset.count} entries, "
                f"{dataset.total_duration:.2f}s total"
            )
            
            logger.info(f"Pipeline completed successfully for {metadata.video_id}")
            
            return PipelineResult(
                video_id=metadata.video_id,
                audio_path=audio_file.path,
                transcript_path=transcript.path,
                dataset_path=dataset.path,
                status="success",
                messages=messages
            )
            
        except PipelineError as e:
            logger.error(f"Pipeline failed: {e}")
            return PipelineResult(
                video_id=metadata.video_id if 'metadata' in locals() else "unknown",
                status="failed",
                error=str(e),
                messages=messages
            )
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return PipelineResult(
                video_id="unknown",
                status="failed",
                error=f"Unexpected error: {e}",
                messages=messages
            )
