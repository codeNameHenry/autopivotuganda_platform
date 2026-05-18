# Dockerfile for FastAPI services
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY services/listing-service/requirements.txt /app/requirements.txt
COPY services/listing-service /app/services/listing-service
COPY shared /app/shared

ENV PYTHONPATH=/app

RUN pip install --no-cache-dir --default-timeout=120 --retries 10 -r /app/requirements.txt

WORKDIR /app/services/listing-service

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
