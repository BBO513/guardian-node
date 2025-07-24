# Dockerfile for Guardian Node & Family Assistant
# Raspberry Pi 5 compatible (ARM64) with fallback to x86_64
FROM python:3.9-slim
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc python3-dev curl libportaudio2 portaudio19-dev git cmake make && rm -rf /var/lib/apt/lists/*
COPY ../guardian_interpreter/requirements.txt .
ENV CMAKE_ARGS="-DGGML_NO_ACCELERATE=ON -DGGML_NATIVE=OFF -DGGML_ARM_DOTPROD=OFF -DGGML_ARM_I8MM=OFF -DGGML_ARM_SVE=OFF -DGGML_ARM_SME=OFF -DGGML_ARM_FMA=OFF -DGGML_ARM_FP16=OFF -DGGML_ARM=OFF"
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt
COPY .. .
RUN mkdir -p /app/logs /app/data /app/models
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 GUARDIAN_OFFLINE_MODE=1
ENV PYTHONPATH=/app
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD /bin/bash -c "curl -f http://localhost:8080/health || exit 1"
CMD ["python3", "guardian_interpreter/main.py", "--mcp", "--family-mode"]
