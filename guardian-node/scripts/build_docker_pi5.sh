#!/bin/bash
# Script to build and run Guardian Node Docker container on Raspberry Pi 5
# This script should be run on the Raspberry Pi 5 itself

set -e  # Exit on error

echo "Building Guardian Node Docker image for ARM64 (Raspberry Pi 5)..."

# Build the Docker image for ARM64
docker buildx build \
  --platform linux/arm64 \
  -t guardian-node:v1.0.0 \
  . \
  --load

echo "Docker image built successfully!"
echo "Image details:"
docker images | grep guardian-node

echo "Starting Guardian Node container with docker-compose..."
docker-compose up -d

echo "Container started! Status:"
docker-compose ps

echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop the container:"
echo "  docker-compose down"
echo ""
echo "To access the web interface:"
echo "  http://localhost:8080"