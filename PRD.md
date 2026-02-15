# PRD: Agentic YouTube-to-Speech Dataset Generator

## 1. Problem Statement

### Background
High-quality speech datasets are a critical requirement for training Automatic Speech Recognition (ASR) and Text-to-Speech (TTS) models. While English has abundant, well-curated datasets, **low-resource languages like Urdu suffer from a severe lack of clean, sentence-aligned speech data**.

Currently, creating such datasets involves multiple manual or semi-automated steps:
- Downloading videos
- Extracting audio
- Transcribing speech
- Segmenting audio by sentences
- Cleaning and filtering noisy samples
- Structuring the final dataset for training

This process is **time-consuming, error-prone, and cannot be solved using a single LLM prompt** because it requires:
- Multi-step orchestration
- Tool usage (audio processing, ASR, VAD)
- Conditional decision-making (quality checks, language routing)

### Problem Statement
There is no agentic system that can **autonomously convert raw YouTube videos into a structured, high-quality speech dataset**, particularly for **Urdu**, by reasoning over multiple steps, interacting with external tools, and enforcing quality boundaries.

This project aims to solve that bottleneck.

---

## 2. Use Case Selection

### Industry Vertical
**AI / Speech Technology (Machine Learning Infrastructure)**

### Agentic Use Case
An **Agentic Dataset Generation System** that takes a YouTube video link as input and produces a **sentence-level speech dataset** suitable for ASR and TTS training.

This use case requires:
- Multi-stage perception (audio, language, timestamps)
- Reasoned planning (which tools to call, what to discard)
- Execution via Python tools (audio slicing, transcription, database writes)

---

## 3. User Personas

### Primary User
**Speech ML Researcher / AI Engineer**
- Working on ASR or TTS models
- Needs large-scale, clean, aligned speech-text data
- Especially focused on Urdu or other low-resource languages

### Secondary User
**Academic Student / Research Lab**
- Creating datasets for experiments or final-year projects
- Needs reproducible, automated dataset pipelines

---

## 4. Goals & Non-Goals

### Goals
- Automatically process a YouTube video into sentence-level audio segments
- Generate aligned `(audio, text)` pairs
- Store results in a structured database/table
- Support English initially, with extensibility to Urdu
- Enforce quality constraints (duration, silence, confidence)

### Non-Goals
- Hosting or redistributing copyrighted datasets
- Real-time transcription
- Model training itself (focus is dataset generation)

---

## 5. Success Metrics

### Quantitative Metrics
- % of usable audio segments after filtering
- Average utterance duration within target range (1–12s)
- ASR confidence score distribution
- Total dataset hours generated per video

### Qualitative Metrics
- Dataset readiness for ASR/TTS training
- Reduction in manual preprocessing effort
- Stability across different video domains (news, podcasts, lectures)

---

## 6. Agentic Boundary Definition

### Agent Goal
Convert a raw YouTube video into a **clean, structured speech dataset**.

### Agent Toolbox
The agent is allowed to:
- Download and process audio
- Call ASR and VAD models
- Write to local storage and databases

The agent is **not allowed** to:
- Upload copyrighted media
- Modify external systems without explicit tools

---

## 7. Tool & Data Inventory (External World)

### Knowledge Sources
- Pretrained ASR models (English / Urdu)
- Voice Activity Detection (VAD) model
- Language identification model
- Local metadata database (SQLite / CSV / Parquet)

### Action Tools (Python Functions)

| Tool Name | Description |
|---------|------------|
| `download_youtube_audio(url)` | Extracts audio from video |
| `normalize_audio(path)` | Resamples and normalizes audio |
| `detect_language(audio)` | Detects spoken language |
| `run_vad(audio)` | Identifies speech segments |
| `transcribe_audio(audio)` | Generates transcript with timestamps |
| `segment_audio(audio, timestamps)` | Cuts sentence-level audio |
| `quality_filter(segment)` | Drops noisy/short samples |
| `store_dataset_row()` | Writes data to DB/table |

---

## 8. LangGraph-Based System Architecture

### High-Level Agent Flow

1. **Input Node**
   - Accepts YouTube URL

2. **Audio Intake Agent**
   - Downloads and normalizes audio

3. **Language Detection Agent**
   - Routes to English or Urdu ASR pipeline

4. **Transcription Agent**
   - Produces timestamped text

5. **Segmentation Agent**
   - Splits audio into sentence-level chunks

6. **Quality Control Agent**
   - Filters based on duration, silence, confidence

7. **Dataset Builder Agent**
   - Stores `(id, audio_path, transcript, metadata)` in DB

Each agent is a node in **LangGraph**, with conditional edges for retries, rejection, or routing.

---

## 9. Output Artifacts

### Dataset Table Schema

| Column Name | Description |
|------------|------------|
| `id` | Unique segment ID |
| `video_id` | Source YouTube video |
| `start_time` | Segment start (seconds) |
| `end_time` | Segment end (seconds) |
| `audio_path` | File location |
| `text` | Transcript |
| `language` | en / ur |
| `confidence` | ASR confidence score |

---

## 10. Risks & Mitigations

| Risk | Mitigation |
|----|-----------|
| Noisy YouTube audio | VAD + confidence filtering |
| Mixed-language speech | Language detection + routing |
| Copyright concerns | Store metadata + regeneration scripts |
| Urdu ASR quality | Domain filtering + post-cleaning |

---

## 11. Why This Must Be Agentic

This system **cannot be implemented as a single prompt** because it requires:
- Sequential decision-making
- Tool invocation
- Conditional branching
- Persistent state across steps

LangGraph enables:
- Explicit agent boundaries
- Robust execution graphs
- Production-grade orchestration

---

## 12. Project Value Summary

This project delivers a **scalable, reusable, and language-aware dataset generation pipeline**, addressing a real bottleneck in speech AI—especially for **Urdu and other low-resource languages**.

It demonstrates:
- Agentic reasoning
- Tool-based execution
- Industrial ML system design
