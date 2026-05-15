"""CLI entry point for pipeline execution."""
import sys
import asyncio
from pathlib import Path

from src.core.logging import setup_logging
from src.schemas.models import PipelineRequest
from src.services.pipeline_orchestrator import PipelineOrchestrator

# Setup logging
logger = setup_logging()


async def main():
    """Main CLI entry point."""
    if len(sys.argv) != 2:
        print("Usage: python -m src.main_cli <youtube_url>")
        sys.exit(1)
    
    youtube_url = sys.argv[1]
    
    print(f"Starting pipeline for URL: {youtube_url}\n")
    
    # Create request
    request = PipelineRequest(youtube_url=youtube_url)
    
    # Execute pipeline
    orchestrator = PipelineOrchestrator()
    result = await orchestrator.execute(request)
    
    # Print results
    print("\n" + "="*60)
    print("PIPELINE RESULTS")
    print("="*60)
    print(f"Status: {result.status}")
    print(f"Video ID: {result.video_id}")
    
    if result.status == "success":
        print(f"\nAudio: {result.audio_path}")
        print(f"Transcript: {result.transcript_path}")
        print(f"Dataset: {result.dataset_path}")
        
        print("\nPipeline Log:")
        for msg in result.messages:
            print(f"  • {msg}")
    else:
        print(f"\nError: {result.error}")
    
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
