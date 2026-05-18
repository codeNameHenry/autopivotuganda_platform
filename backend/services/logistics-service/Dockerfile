FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y gcc libpq-dev curl && rm -rf /var/lib/apt/lists/*

COPY services/logistics-service/requirements.txt /app/requirements.txt
COPY services/logistics-service /app/services/logistics-service
COPY shared /app/shared

ENV PYTHONPATH=/app

RUN pip install --no-cache-dir --default-timeout=120 --retries 10 -r /app/requirements.txt

WORKDIR /app/services/logistics-service

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
