<<<<<<< HEAD
# Dockerfile for Guardian Node & Family Assistant
# Raspberry Pi 5 compatible (ARM64) with fallback to x86_64
FROM python:3.11-slim

# Set metadata
LABEL maintainer="Guardian Team"
LABEL description="Guardian Node Family Cybersecurity Assistant"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV GUARDIAN_CONTAINER=true
ENV GUARDIAN_DATA_PATH=/data
ENV GUARDIAN_LOGS_PATH=/logs

# Set working directory
WORKDIR /app

# Install system dependencies (includes portaudio19-dev for PyAudio/speech support)
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    wget \
    iputils-ping \
    net-tools \
    procps \
    htop \
    nano \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r guardian && useradd -r -g guardian guardian

# Create directories for persistent data
RUN mkdir -p /data /logs /app/models && \
    chown -R guardian:guardian /data /logs /app

# Copy requirements first for better Docker layer caching
COPY guardian_interpreter/requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY guardian_interpreter/ /app/guardian_interpreter/
COPY *.md /app/
COPY *.py /app/

# Copy Docker-specific files
COPY docker/ /app/docker/

# Set proper permissions
RUN chown -R guardian:guardian /app && \
    chmod +x /app/docker/*.sh

# Create health check script
COPY docker/health_check.py /app/health_check.py
RUN chmod +x /app/health_check.py

# Persistent volumes for data and logs
VOLUME ["/data", "/logs", "/app/models"]

# Health check configuration
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python /app/health_check.py || exit 1

# Expose ports
EXPOSE 8080 8443

# Switch to non-root user
USER guardian

# Set the entry point
ENTRYPOINT ["/app/docker/entrypoint.sh"]

# Default command
CMD ["python", "/app/guardian_interpreter/main.py"]
=======
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git-lfs \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY guardian_interpreter/ ./guardian_interpreter/
COPY assets/ ./assets/

# Set working directory and run
WORKDIR /app/guardian_interpreter
CMD ["python3", "main.py", "--mcp", "--family-mode"]
>>>>>>> a0d2c75a88747ce742b9ef6cc664642fcb07ac5e
