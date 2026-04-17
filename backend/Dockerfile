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

<<<<<<< HEAD
# Cloud Run uses PORT=8080 by default
ENV PORT=8080
=======
# This ensures all your internal imports work
ENV PYTHONPATH=. 
>>>>>>> a049d96a5ac6484910a136cc962ef4ffe77b1cf2

# Cloud Run injects $PORT (usually 8080), so we use that variable
CMD exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1 --proxy-headers
