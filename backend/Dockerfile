# Use official Python image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app_root

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Copy requirements first (for better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything from your local directory into /app_root
# If you are running this from INSIDE the Backend folder, use '.' 
# If you are running from one level up, use 'backend/'
COPY . .

# CRITICAL: Force the PYTHONPATH to app_root
# This ensures 'import app.main' works from anywhere in the container
ENV PYTHONPATH=/app_root
ENV PYTHONUNBUFFERED=1

# Cloud Run injects $PORT. Using the list format ["uvicorn", ...] is 
# preferred for better signal handling (SIGTERM).
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080} --workers 1 --proxy-headers --timeout-keep-alive 65"]