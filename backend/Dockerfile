# Use official Python image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app_root

# Install system dependencies (required for psycopg2-binary, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip first
RUN pip install --no-cache-dir --upgrade pip

# Copy requirements from ROOT (build context is branch root)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all backend code (inside 'backend/' folder of the context)
# ... (after your pip installs)
COPY backend/ .

# This ensures all your internal imports work
ENV PYTHONPATH=.

# Ensure stdout/stderr are unbuffered for Cloud Run logging
ENV PYTHONUNBUFFERED=1

# Cloud Run injects $PORT (usually 8080), so we use that variable
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080} --workers 1 --proxy-headers --timeout-keep-alive 65

# Health check - lightweight, doesn't depend on database
# Initial delay: 10 seconds, interval: 5 seconds, timeout: 3 seconds, retries: 3
HEALTHCHECK --start-period=10s --interval=5s --timeout=3s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8080}/health || exit 1