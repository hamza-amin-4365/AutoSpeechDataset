Lab 7 (Evaluation)

* src/test_dataset.json — 20 Q&A pairs covering all pipeline aspects
* src/run_eval.py — headless eval script with sys.exit(0/1) CI exit codes, Judge LLM scoring for faithfulness + relevancy
* src/eval_threshold_config.json — {"min_faithfulness": 0.75, "min_relevancy": 0.75}

Lab 8 (FastAPI)

* src/schema.py — Pydantic ChatRequest / ChatResponse models
* src/api.py — POST /chat (sync) + POST /stream (SSE streaming via graph.stream())

Lab 9 (Docker)

* Dockerfile — python:3.12-slim, layer-optimized (deps first, code after)
* .dockerignore — excludes .env, .venv, __pycache__, .db files, etc.
* docker-compose.yaml — agent service on port 8000 + ChromaDB on 8001, persistent volumes
* docker_build.log — sample build/up/ps output

Lab 10 (CI/CD)

* .github/workflows/main.yml — triggers on push to main, runs eval script with GitHub Secrets

Lab 11 (Drift Monitoring)

* src/feedback_db.py — SQLite schema with all required columns
* src/app.py — Streamlit UI with 👍/👎 feedback, comment box, session state
* src/analyze_feedback.py — Judge LLM categorizes failures into Hallucination/Tool Error/etc.
* src/feedback_log.db — seeded with 12 interactions (7 positive, 5 negative)
* drift_report.md — analysis summary
* improved_prompt.txt — revised system prompt based on failure findings