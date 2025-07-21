# Guardian Node Docker Enhancements

## Overview

This document outlines the enhanced Docker configuration for the Guardian Node Family AI Assistant. The updated configuration provides better resource management, monitoring capabilities, and environment variable control for the LLM integration.

## Key Enhancements

### 1. Optimized Container Configuration

```yaml
guardian-node:
  build: .
  container_name: guardian-node-family-assistant
  ports:
    - "8080:8080"     # Health/API endpoint and GUI interface
    - "8080:8080"     # GUI interface
```

- **Unified Port**: Single port (8080) for API/health endpoints and GUI interface
- **Standardized Container Naming**: Clear naming convention for easier management

### 2. Enhanced Volume Management

```yaml
volumes:
  # Mount models directory for GGUF models
  - ./models:/app/models:ro
  # Mount data directory for family profiles and logs
  - ./data:/app/data
  # Mount logs directory
  - ./logs:/app/logs
```

- **Read-Only Model Directory**: Prevents accidental model corruption
- **Simplified Volume Structure**: Clearer organization of data, logs, and models
- **Direct Host Mounting**: Easier access to files for development and debugging

### 3. Environment Variable Configuration

```yaml
environment:
  # LLM Model Configuration
  - GUARDIAN_LLM_MODEL_PATH=/app/models/phi-3-mini-4k-instruct-q4.gguf
  - GUARDIAN_MODELS_DIR=/app/models
  
  # Family Assistant Configuration
  - GUARDIAN_MODE=family
  - GUARDIAN_OFFLINE_MODE=true
  - GUARDIAN_LOG_LEVEL=INFO
  
  # Security Configuration
  - GUARDIAN_ENCRYPT_DATA=true
  - GUARDIAN_AUDIT_LOGGING=true
  
  # Performance Configuration (Raspberry Pi optimized)
  - GUARDIAN_MAX_MEMORY_MB=2048
  - GUARDIAN_CPU_THREADS=4
  - GUARDIAN_MODEL_CACHE_SIZE=512
```

- **Categorized Configuration**: Clearly organized by functional area
- **LLM-Specific Settings**: Direct control over model paths and directories
- **Performance Tuning**: Raspberry Pi-optimized memory and CPU settings
- **Security Controls**: Explicit security configuration options

### 4. Resource Management

```yaml
deploy:
  resources:
    limits:
      memory: 3G
      cpus: '3.0'
    reservations:
      memory: 1G
      cpus: '1.0'
```

- **Memory Limits**: Prevents container from consuming excessive RAM
- **CPU Allocation**: Balanced CPU usage for Raspberry Pi deployment
- **Resource Reservations**: Ensures minimum resources for stable operation

### 5. Health Monitoring

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

- **HTTP-Based Health Checks**: Modern health check approach using HTTP endpoint
- **Optimized Timing**: Faster health check intervals with appropriate timeouts
- **Startup Grace Period**: Allows for model loading time before health checks

### 6. Prometheus Monitoring Integration

```yaml
guardian-monitor:
  image: prom/prometheus:latest
  container_name: guardian-monitor
  ports:
    - "9090:9090"
  volumes:
    - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
```

- **Optional Monitoring**: Using Docker profiles for conditional deployment
- **Prometheus Integration**: Professional-grade metrics collection
- **Custom Configuration**: Tailored Prometheus setup for Guardian Node metrics

## Usage Instructions

### Starting the Basic Service

```bash
docker-compose up -d
```

### Starting with Monitoring

```bash
docker-compose --profile monitoring up -d
```

### Checking Container Health

```bash
# View container status
docker ps

# Check health status
curl http://localhost:8080/health

# View metrics
curl http://localhost:8000/metrics
```

### Accessing Prometheus Dashboard

Open `http://localhost:9090` in your browser to access the Prometheus dashboard.

## Environment Variable Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `GUARDIAN_LLM_MODEL_PATH` | Path to the primary GGUF model | `/app/models/phi-3-mini-4k-instruct-q4.gguf` |
| `GUARDIAN_MODELS_DIR` | Directory containing all GGUF models | `/app/models` |
| `GUARDIAN_MODE` | Operating mode (family, standard) | `family` |
| `GUARDIAN_OFFLINE_MODE` | Whether to operate in offline-only mode | `true` |
| `GUARDIAN_LOG_LEVEL` | Logging verbosity | `INFO` |
| `GUARDIAN_ENCRYPT_DATA` | Whether to encrypt stored data | `true` |
| `GUARDIAN_AUDIT_LOGGING` | Whether to enable detailed audit logging | `true` |
| `GUARDIAN_MAX_MEMORY_MB` | Maximum memory for LLM models | `2048` |
| `GUARDIAN_CPU_THREADS` | CPU threads for LLM inference | `4` |
| `GUARDIAN_MODEL_CACHE_SIZE` | Size of model cache in MB | `512` |

## Integration with LLM Loader

The Docker configuration is designed to work seamlessly with the enhanced LLM Loader system. The environment variables control:

1. Model discovery via `GUARDIAN_MODELS_DIR`
2. Default model selection via `GUARDIAN_LLM_MODEL_PATH`
3. Memory constraints via `GUARDIAN_MAX_MEMORY_MB`
4. Performance tuning via `GUARDIAN_CPU_THREADS` and `GUARDIAN_MODEL_CACHE_SIZE`

The health check endpoint provides visibility into:
- Available models
- Currently loaded model
- System resource usage
- Overall system health

## Raspberry Pi Optimization

This configuration is specifically optimized for Raspberry Pi 5 deployment:

- Memory limits set to 3GB (leaving room for system)
- CPU allocation balanced for quad-core Pi 5
- Reduced model cache size for efficient operation
- Health check timing adjusted for ARM performance characteristics