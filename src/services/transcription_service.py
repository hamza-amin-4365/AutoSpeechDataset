"""Deepgram transcription service with Urdu support."""
import asyncio
from pathlib import Path
from typing import Optional

from deepgram import DeepgramClient

from src.core.config import get_settings
from src.core.exceptions import TranscriptionError
from src.core.logging import get_logger
from src.schemas.models import Transcript, TranscriptSegment, AudioFile
from src.utils.file_helpers import write_json_async, read_json_async

logger = get_logger("transcription_service")
settings = get_settings()


class TranscriptionService:
    """Handles audio transcription using Deepgram Nova-3."""
    
    def __init__(self):
        self.settings = settings
        self.transcript_dir = settings.transcript_dir
        self.client = DeepgramClient(api_key=settings.deepgram_api_key)
        
    async def transcribe(
        self,
        audio_file: AudioFile,
        force: bool = False
    ) -> Transcript:
        """Transcribe audio file to text with timestamps.
        
        Args:
            audio_file: AudioFile object with path
            force: Force re-transcription even if cached
            
        Returns:
            Transcript object with segments
            
        Raises:
            TranscriptionError: If transcription fails
        """
        try:
            transcript_path = self.transcript_dir / f"{audio_file.video_id}.json"
            
            # Check cache
            if transcript_path.exists() and not force:
                logger.info(f"Using cached transcript: {transcript_path}")
                segments_data = await read_json_async(transcript_path)
                segments = [TranscriptSegment(**seg) for seg in segments_data]
                return Transcript(
                    video_id=audio_file.video_id,
                    path=transcript_path,
                    segments=segments,
                    language=settings.transcription_language
                )
            
            # Transcribe with retries
            for attempt in range(settings.max_retries):
                try:
                    segments = await self._transcribe_with_deepgram(audio_file.path)
                    break
                except Exception as e:
                    if attempt == settings.max_retries - 1:
                        raise
                    logger.warning(f"Transcription attempt {attempt + 1} failed: {e}")
                    await asyncio.sleep(settings.retry_delay * (attempt + 1))
            
            # Save transcript
            segments_data = [seg.model_dump() for seg in segments]
            await write_json_async(transcript_path, segments_data)
            
            transcript = Transcript(
                video_id=audio_file.video_id,
                path=transcript_path,
                segments=segments,
                language=settings.transcription_language
            )
            
            logger.info(f"Transcribed audio: {len(segments)} segments")
            return transcript
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise TranscriptionError(f"Failed to transcribe audio: {e}")
    
    async def _transcribe_with_deepgram(self, audio_path: Path) -> list[TranscriptSegment]:
        """Execute Deepgram transcription."""
        try:
            # Read audio file
            with open(audio_path, "rb") as audio:
                buffer_data = audio.read()
            
            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.listen.v1.media.transcribe_file(
                    request=buffer_data,
                    model=settings.transcription_model,
                    smart_format=True,
                    utterances=True,
                    language=settings.transcription_language,
                )
            )
            
            # Extract segments from response
            segments = self._extract_segments(response)
            
            return segments
            
        except Exception as e:
            logger.error(f"Deepgram API error: {e}")
            raise TranscriptionError(f"Deepgram transcription failed: {e}")
    
    def _extract_segments(self, response) -> list[TranscriptSegment]:
        """Extract and validate segments from Deepgram response."""
        segments = []
        
        try:
            channel = response.results.channels[0]
            alternative = channel.alternatives[0]
            
            # Try to use utterances first (better segmentation)
            if hasattr(alternative, 'utterances') and alternative.utterances:
                for utt in alternative.utterances:
                    if utt.transcript.strip():
                        segments.append(TranscriptSegment(
                            start=utt.start,
                            end=utt.end,
                            text=utt.transcript.strip()
                        ))
            else:
                # Fallback: chunk words into segments
                words = alternative.words
                chunk_size = 15
                
                for i in range(0, len(words), chunk_size):
                    chunk = words[i:i + chunk_size]
                    if chunk:
                        text = " ".join([w.word for w in chunk]).strip()
                        if text:
                            segments.append(TranscriptSegment(
                                start=chunk[0].start,
                                end=chunk[-1].end,
                                text=text
                            ))
            
            logger.info(f"Extracted {len(segments)} segments from transcription")
            return segments
            
        except Exception as e:
            logger.error(f"Failed to extract segments: {e}")
            raise TranscriptionError(f"Segment extraction failed: {e}")
