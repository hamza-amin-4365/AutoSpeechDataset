"""Dataset processing and filtering service."""
from pathlib import Path

from src.core.config import get_settings
from src.core.exceptions import DatasetBuildError
from src.core.logging import get_logger
from src.schemas.models import Dataset, DatasetEntry, Transcript, AudioFile
from src.utils.file_helpers import write_json_async

logger = get_logger("processing_service")
settings = get_settings()


class ProcessingService:
    """Handles dataset creation and audio segment filtering."""
    
    def __init__(self):
        self.settings = settings
        self.dataset_dir = settings.dataset_dir
        self.min_duration = settings.min_segment_duration
        self.max_duration = settings.max_segment_duration
    
    async def build_dataset(
        self,
        transcript: Transcript,
        audio_file: AudioFile
    ) -> Dataset:
        """Build filtered dataset from transcript and audio.
        
        Args:
            transcript: Transcript with segments
            audio_file: Source audio file
            
        Returns:
            Dataset object with filtered entries
            
        Raises:
            DatasetBuildError: If dataset creation fails
        """
        try:
            # Filter segments by duration
            filtered_segments = [
                seg for seg in transcript.segments
                if self.min_duration <= seg.duration <= self.max_duration
            ]
            
            logger.info(
                f"Filtered {len(filtered_segments)}/{len(transcript.segments)} "
                f"segments (duration: {self.min_duration}-{self.max_duration}s)"
            )
            
            # Create dataset entries
            entries = []
            total_duration = 0.0
            
            for i, seg in enumerate(filtered_segments):
                entry = DatasetEntry(
                    id=f"{audio_file.video_id}_{i}",
                    audio_path=audio_file.path,
                    start=seg.start,
                    end=seg.end,
                    text=seg.text,
                    duration=seg.duration
                )
                entries.append(entry)
                total_duration += seg.duration
            
            # Save dataset
            dataset_path = self.dataset_dir / f"{audio_file.video_id}_dataset.json"
            dataset_data = {
                "video_id": audio_file.video_id,
                "total_entries": len(entries),
                "total_duration": total_duration,
                "entries": [entry.model_dump(mode='json') for entry in entries]
            }
            
            await write_json_async(dataset_path, dataset_data)
            
            dataset = Dataset(
                video_id=audio_file.video_id,
                path=dataset_path,
                entries=entries,
                total_duration=total_duration
            )
            
            logger.info(
                f"Built dataset: {len(entries)} entries, "
                f"{total_duration:.2f}s total duration"
            )
            
            return dataset
            
        except Exception as e:
            logger.error(f"Dataset build failed: {e}")
            raise DatasetBuildError(f"Failed to build dataset: {e}")
