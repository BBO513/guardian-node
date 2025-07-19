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
