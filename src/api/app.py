"""FastAPI application setup."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router
from src.core.logging import setup_logging

# Setup logging
setup_logging()

# Create FastAPI app
app = FastAPI(
    title="Speech Dataset Pipeline",
    description="Production-grade YouTube to Speech Dataset automation service",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api/v1", tags=["pipeline"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Speech Dataset Pipeline",
        "version": "2.0.0",
        "status": "running"
    }
