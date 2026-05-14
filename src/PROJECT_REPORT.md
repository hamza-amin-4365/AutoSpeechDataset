# AutoSpeechDataset - Complete Project Report

## 1. Project Overview

**AutoSpeechDataset** is an agentic pipeline that converts YouTube videos into structured speech datasets for ASR (Automatic Speech Recognition) and TTS (Text-to-Speech) model training. The system is particularly focused on low-resource languages like Urdu.

### Key Features
- YouTube audio extraction (16kHz mono WAV)
- Deepgram Nova-3 transcription with Urdu language support
- Sentence-level audio segmentation (1-12 seconds duration filter)
- LangGraph-based multi-agent orchestration
- Security guardrails with input validation and output sanitization
- Human-in-the-loop approval workflow
- Feedback collection and drift monitoring
- CI/CD evaluation pipeline with Judge LLM scoring

---

## 2. Architecture

### High-Level Flow
```
YouTube URL → Guardrail Check → Executor Agent → RAG Context → Analyst Agent → HITL Approval → Dataset
```

### Agent Nodes
| Node | Role | Tools |
|------|------|-------|
| `guardrail` | Input validation | Deterministic keyword/pattern checking |
| `executor` | Audio Processing Specialist | download_audio, transcribe_audio, fetch_youtube_metadata |
| `rag` | Context injection | FAISS vector search on PRD.md |
| `analyst` | Dataset Builder | build_dataset |
| `approval` | Human review | Manual y/n input |

---

## 3. Source Code Structure

### Core Pipeline
| File | Purpose |
|------|---------|
| `multi_agent_graph.py` | Main LangGraph workflow with state management |
| `secured_graph.py` | Security-enhanced version with guardrail nodes |
| `agent_factory.py` | Agent creation using LangChain's tool-calling agent |
| `agents_config.py` | Agent configurations and tool bindings |

### Tools & Utilities
| File | Purpose |
|------|---------|
| `tools.py` | YouTube download (yt-dlp), Deepgram transcription, dataset building |
| `rag.py` | FAISS-based RAG for PRD context retrieval |
| `schema.py` | Pydantic models for API request/response |
| `guardrails_config.py` | Input validation, output sanitization, PII detection |

### API & UI
| File | Purpose |
|------|---------|
| `api.py` | FastAPI with /health, /chat (sync), /stream (SSE) endpoints |
| `app.py` | Streamlit UI with feedback collection |

### Quality & Security
| File | Purpose |
|------|---------|
| `run_eval.py` | Headless evaluation with Judge LLM (Groq Llama 3.3) |
| `adversarial_tests.py` | Security guardrail testing suite |
| `feedback_db.py` | SQLite feedback logging |
| `analyze_feedback.py` | Drift monitoring with failure categorization |
| `seed_feedback.py` | Sample feedback data for testing |

### Data Files
| File | Purpose |
|------|---------|
| `test_dataset.json` | 20 test queries with reference answers for evaluation |
| `eval_threshold_config.json` | Faithfulness ≥0.75, Relevancy ≥0.75 |
| `checkpoint_db.sqlite` | LangGraph state persistence |
| `feedback_log.db` | User feedback storage |

---

## 4. Security Implementation

### Input Guardrails
- **Forbidden keywords**: jailbreak patterns, SQL injection, command injection
- **Suspicious patterns**: hidden HTML comments, template injection
- **Whitelist validation**: Only YouTube/audio/dataset related topics allowed

### Output Sanitization
- **Path redaction**: /home/, /root/, C:\, relative paths
- **Metadata redaction**: sqlite_sequence, __metadata__
- **Timestamp redaction**: ISO format timestamps
- **PII detection**: Email, phone, IP address patterns

### Adversarial Test Coverage
- DAN persona bypass attempts
- Payload smuggling (hidden commands)
- Instruction hijacking
- Obfuscation (leetspeak, synonyms)

---

## 5. Docker Configuration

### Dockerfile
```dockerfile
FROM python:3.12-slim
WORKDIR /app
RUN apt-get install ffmpeg
COPY requirements.txt && pip install --no-cache-dir --retries 10
COPY src/ ./src/
EXPOSE 8000
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yaml
| Service | Image | Ports | Volumes |
|---------|-------|-------|---------|
| `agent` | Custom build | 8000:8000 | audio-data, transcript-data, dataset-data |
| `vectordb` | chromadb/chroma | 8001:8000 | chroma-data |

---

## 6. CI/CD Pipeline

### GitHub Actions Workflow (`.github/workflows/main.yml`)

**Trigger**: Push to main, Pull Request to main

**Steps**:
1. Checkout code
2. Set up Python 3.12
3. Install ffmpeg system dependency
4. Install Python dependencies from requirements.txt
5. Run headless evaluation (`src/run_eval.py`)
6. Upload eval results artifact

**Environment Variables**:
- `GROQ_API_KEY`: LLM provider for agents and Judge
- `DEEPGRAM_API_KEY`: Speech-to-text transcription
- `EVAL_DATASET_PATH`: src/test_dataset.json
- `EVAL_THRESHOLD_PATH`: src/eval_threshold_config.json

**Exit Codes**:
- `0`: Pass (scores above threshold)
- `1`: Fail (scores below threshold)

---

## 7. Dependencies

### Core
- `langgraph>=0.2.0` - Agent orchestration
- `langchain-groq>=0.2.0` - Groq LLM integration
- `deepgram-sdk>=6.0.1` - Speech recognition
- `yt-dlp>=2026.2.21` - YouTube download
- `fastapi>=0.115.0` + `uvicorn>=0.30.0` - API server
- `streamlit>=1.40.0` - Web UI

### Vector & Embeddings
- `faiss-cpu` - Vector similarity search
- `sentence-transformers` - Embedding generation (all-MiniLM-L6-v2)

### Storage
- `langgraph-checkpoint-sqlite>=0.1.0` - State persistence
- `sqlite3` (stdlib) - Feedback logging

---

## 8. Dataset Output Format

Each dataset entry contains:
```json
{
  "id": "{video_id}_{segment_index}",
  "audio_path": "path/to/audio.wav",
  "start": 0.5,
  "end": 5.2,
  "text": "Transcribed Urdu text",
  "duration": 4.7
}
```

**Filters applied**:
- Duration: 1-12 seconds only
- Language: Urdu (Deepgram language='ur')

---

## 9. Evaluation System

### Judge LLM Scoring
- **Model**: Groq Llama 3.3 70B Versatile
- **Metrics**:
  - Faithfulness (0.0-1.0): Factual consistency with reference
  - Relevancy (0.0-1.0): Addresses the question

### Drift Monitoring
- Categorizes negative feedback using Judge LLM
- Categories: Hallucination, Tool Error, Wrong Tone, Incomplete Response, Pipeline Failure, Other
- Generates drift report (drift_report.md)

---

## 10. Running the Project

### Local Development
```bash
uv sync
uv run src/api.py  # API server on port 8000
uv run src/app.py  # Streamlit UI
```

### Docker
```bash
docker-compose up --build
```

### CLI
```bash
python src/main.py "https://youtube.com/watch?v=..."
```

### Evaluation
```bash
python src/run_eval.py
python src/adversarial_tests.py
```

---

## 11. Security Test Results

The adversarial test suite validates:
- 12+ attack vectors covering persona bypass, payload smuggling, instruction hijacking
- Output sanitization for paths, timestamps, metadata
- PII detection for email, phone, IP addresses

---

## 12. Known Limitations

- Human-in-the-loop approval requires interactive input (not suitable for fully automated runs)
- Deepgram API key required for transcription
- Urdu language hardcoded in transcription tool
- ChromaDB service defined but not used (FAISS used instead for RAG)

---
