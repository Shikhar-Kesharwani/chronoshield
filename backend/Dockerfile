FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (required for psycopg2 and sklearn)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cloud platforms like Render inject the PORT environment variable.
ENV PORT=8000
EXPOSE ${PORT}

# Use shell form to allow $PORT evaluation
CMD uvicorn api:app --host 0.0.0.0 --port $PORT
