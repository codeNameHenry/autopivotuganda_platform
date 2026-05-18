FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y gcc libpq-dev curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --default-timeout=120 --retries 10 -r requirements.txt

COPY . /app

EXPOSE 8000
CMD ["uvicorn", "api_gateway:app", "--host", "0.0.0.0", "--port", "8000"]
