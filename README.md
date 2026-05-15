# Speech Dataset Pipeline

Production-grade YouTube to Speech Dataset automation service.

## Install

```bash
uv sync
```

## Usage

```bash
# CLI
uv run python -m src.main_cli "https://youtube.com/watch?v=VIDEO_ID"

# API
uv run uvicorn src.api.app:app --reload
```

## Config

Create `.env`:
```
DEEPGRAM_API_KEY=your_key
```
