# CogniTutor AI Learning Platform - Production Container
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Install system dependencies (for building any C-extensions if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Ensure data and uploads directories exist with proper permissions
RUN mkdir -p /app/data /app/uploads /app/sample_materials

EXPOSE 8000

# Run uvicorn server binding to 0.0.0.0
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
