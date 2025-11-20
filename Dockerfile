# Dockerfile for Guardian Node & Family Assistant
# Raspberry Pi 5 compatible (ARM64) with fallback to x86_64

FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    python3-dev \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/models

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV GUARDIAN_OFFLINE_MODE=1

# Health check - Simple Python-based check without external dependencies
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import sys; import os; sys.exit(0 if os.path.exists('/app/logs/health_status.json') else 1)" || exit 1

# Run the application
CMD ["tail", "-f", "/dev/null"]