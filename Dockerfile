# ─── Render Deployment Dockerfile ───
# Uses Python 3.11-slim with ffmpeg for Whisper audio transcription

FROM python:3.11-slim

# Install system dependencies (ffmpeg for Whisper audio processing)
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (Docker cache optimization)
COPY blog_summarizer/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY blog_summarizer/backend/ ./backend/

# Copy frontend code (served by FastAPI)
COPY blog_summarizer/frontend/ ./frontend/

# Set working directory to backend
WORKDIR /app/backend

# Expose port (Render sets $PORT dynamically)
EXPOSE 10000

# Start server — Render injects $PORT env var
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}"]
