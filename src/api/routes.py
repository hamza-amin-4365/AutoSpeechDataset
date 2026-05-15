"""FastAPI routes for the pipeline API."""
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from src.schemas.models import PipelineRequest, PipelineResult
from src.services.pipeline_orchestrator import PipelineOrchestrator
from src.core.logging import get_logger

logger = get_logger("api")
router = APIRouter()

# Initialize orchestrator
orchestrator = PipelineOrchestrator()


@router.post("/process", response_model=PipelineResult)
async def process_video(request: PipelineRequest) -> PipelineResult:
    """Process a YouTube video through the complete pipeline.
    
    Args:
        request: Pipeline request with YouTube URL
        
    Returns:
        Pipeline result with paths and status
    """
    try:
        logger.info(f"Received request for URL: {request.youtube_url}")
        result = await orchestrator.execute(request)
        
        if result.status == "failed":
            logger.warning(f"Pipeline failed: {result.error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.error
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse(
        content={"status": "healthy", "service": "speech-dataset-pipeline"},
        status_code=status.HTTP_200_OK
    )
