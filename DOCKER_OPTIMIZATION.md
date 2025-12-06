# Docker Container Optimization

## Problem
Docker container was too large and failing due to including multiple copies of 1.6GB model files (~10GB total). Additionally, the container was running in interactive CLI mode causing EOF errors.

## Solution Applied

### 1. Updated `.dockerignore`
- Excluded all `.gguf` model files (mounted as volumes instead)
- Excluded test files, documentation, and build scripts
- Excluded Python cache and git files
- Used `**/*.gguf` pattern to catch models in all subdirectories

### 2. Optimized `dockerfile`
- Copy only runtime Python files (not tests/demos)
- Copy only necessary subdirectories
- Models are mounted as volumes, not copied into image
- Reduced layers and improved caching
- Changed CMD to run health_check.py (service mode) instead of main.py (CLI mode)
- Added psutil for resource monitoring

### 3. Results
- **Before**: ~10GB+ (multiple model copies)
- **After**: 869MB (no models in image)
- **Build time**: ~2 seconds (cached)
- **Status**: Running as service with health check endpoint

## How It Works

The model files are now:
1. **Excluded** from Docker build context (via `.dockerignore`)
2. **Mounted** as read-only volumes (via `docker-compose.yml`)
3. **Accessible** at runtime from `/app/models/` inside container

The container runs in service mode:
- Health check server on port 8080
- Endpoints: `/health` and `/metrics`
- No interactive CLI (prevents EOF errors)

## Usage

```bash
# Build the optimized container
docker-compose build

# Run the container (models mounted from host)
docker-compose up -d

# Check health status
curl http://localhost:8080/health

# Check metrics (Prometheus format)
curl http://localhost:8080/metrics

# View logs
docker logs guardian-node-family-assistant

# Check image size
docker images | grep guardian
```

## Health Check Response
```json
{
  "status": "healthy",
  "timestamp": "2025-12-02T18:15:33.105374",
  "version": "1.0.0",
  "mode": "family",
  "resources": {
    "cpu_percent": 5.2,
    "memory_percent": 12.3
  },
  "llm": {
    "available_models": 2,
    "current_model": null,
    "models": ["gemma-2-2b-it-Q4_K_M.gguf", "Phi-3-mini-4k-instruct-q4.gguf"]
  }
}
```

## Key Files Modified
- `dockerfile` - Selective copying, service mode, no model files
- `.dockerignore` - Comprehensive exclusion patterns with `**/*.gguf`
- `docker-compose.yml` - Volume mounts for models (already configured)
