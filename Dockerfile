FROM python:3.12-slim

# Prevent Python from buffering logs and writing bytecode
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# 1. Increased timeout
# 2. Added retries for flaky connections
# 3. Use --no-cache-dir to save space and prevent "reading from server" EOF errors
RUN pip install --no-cache-dir \
    --default-timeout=1000 \
    --retries 10 \
    -r requirements.txt

COPY src/ ./src/
COPY PRD.md .

EXPOSE 8000

# Run from /app to keep internal module paths consistent
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]