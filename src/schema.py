from pydantic import BaseModel, Field
from typing import Optional
import uuid


class ChatRequest(BaseModel):
    message: str = Field(..., description="YouTube URL to process")
    thread_id: str = Field(
        default_factory=lambda: f"pipeline_{uuid.uuid4().hex[:8]}",
        description="Unique thread ID for state persistence",
    )


class ChatResponse(BaseModel):
    thread_id: str
    status: str
    video_id: Optional[str] = None
    transcript_path: Optional[str] = None
    dataset_path: Optional[str] = None
    messages: list[str] = []
    error: Optional[str] = None
