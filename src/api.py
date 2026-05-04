"""
Lab 8: FastAPI wrapper for the AutoSpeechDataset LangGraph pipeline.
Exposes POST /chat (sync) and POST /stream (SSE streaming) endpoints.
"""

import json
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from schema import ChatRequest, ChatResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Import here so the graph + checkpointer are initialized once at startup
    import multi_agent_graph  # noqa: F401 — triggers module-level setup
    yield


app = FastAPI(
    title="AutoSpeechDataset API",
    description="Agentic YouTube-to-Speech Dataset Generator",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Synchronous endpoint. Runs the full pipeline and returns the final state.
    """
    from multi_agent_graph import run_pipeline

    try:
        result = run_pipeline(
            youtube_url=request.message,
            thread_id=request.thread_id,
        )
        return ChatResponse(
            thread_id=request.thread_id,
            status="completed" if not result.get("error") else "failed",
            video_id=result.get("video_id"),
            transcript_path=result.get("transcript_path"),
            dataset_path=result.get("dataset_path"),
            messages=result.get("messages", []),
            error=result.get("error"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/stream")
def stream(request: ChatRequest):
    """
    Streaming endpoint using Server-Sent Events (SSE).
    Yields node-by-node progress as the graph executes.
    """
    from multi_agent_graph import app as graph_app

    initial_state = {
        "youtube_url": request.message,
        "video_id": "",
        "audio_path": "",
        "transcript_path": "",
        "transcript_data": {},
        "dataset_path": "",
        "error": "",
        "messages": [],
        "rag_context": "",
        "hitl_approved": False,
    }
    config = {"configurable": {"thread_id": request.thread_id}}

    def event_generator():
        try:
            for chunk in graph_app.stream(initial_state, config=config):
                for node_name, node_state in chunk.items():
                    data = {
                        "node": node_name,
                        "messages": node_state.get("messages", []),
                        "dataset_path": node_state.get("dataset_path", ""),
                        "error": node_state.get("error", ""),
                    }
                    yield f"data: {json.dumps(data)}\n\n"
            yield "data: {\"node\": \"__end__\", \"status\": \"done\"}\n\n"
        except Exception as e:
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
