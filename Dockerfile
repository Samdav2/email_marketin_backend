# Production Dockerfile for FastAPI Email Marketing Backend
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (default 8000)
EXPOSE 8000

# Run FastAPI app with Uvicorn using dynamic $PORT (required for Railway & Cloud deployment)
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
