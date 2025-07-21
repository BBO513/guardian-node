#!/bin/bash
# Script to verify Guardian Node setup on Raspberry Pi 5
# This script should be run on the Raspberry Pi 5 itself

set -e  # Exit on error

echo "Verifying Guardian Node setup on Raspberry Pi 5..."
echo "=================================================="

# Check OS
echo -n "Checking OS: "
if grep -q "Debian GNU/Linux 12 (bookworm)" /etc/os-release; then
  echo "✅ Debian Bookworm detected"
else
  echo "❌ Not running Debian Bookworm"
  echo "Please install Debian Bookworm on your Raspberry Pi 5"
  exit 1
fi

# Check architecture
echo -n "Checking architecture: "
if [ "$(uname -m)" = "aarch64" ]; then
  echo "✅ ARM64 architecture detected"
else
  echo "❌ Not running on ARM64"
  echo "Please use the 64-bit version of Debian"
  exit 1
fi

# Check Docker
echo -n "Checking Docker: "
if command -v docker &> /dev/null; then
  echo "✅ Docker installed"
else
  echo "❌ Docker not installed"
  echo "Installing Docker..."
  curl -fsSL https://get.docker.com -o get-docker.sh
  sudo sh get-docker.sh
  sudo usermod -aG docker $USER
  echo "Docker installed. Please log out and log back in to use Docker without sudo."
  exit 1
fi

# Check Docker Compose
echo -n "Checking Docker Compose: "
if command -v docker-compose &> /dev/null; then
  echo "✅ Docker Compose installed"
else
  echo "❌ Docker Compose not installed"
  echo "Installing Docker Compose..."
  sudo apt-get update
  sudo apt-get install -y docker-compose
  echo "Docker Compose installed."
fi

# Check Python
echo -n "Checking Python: "
if command -v python3 &> /dev/null; then
  echo "✅ Python installed ($(python3 --version))"
else
  echo "❌ Python not installed"
  echo "Installing Python..."
  sudo apt-get update
  sudo apt-get install -y python3 python3-pip
  echo "Python installed."
fi

# Check Guardian Node files
echo -n "Checking Guardian Node files: "
if [ -f "Dockerfile" ] && [ -f "docker-compose.yml" ]; then
  echo "✅ Guardian Node files found"
else
  echo "❌ Guardian Node files not found"
  echo "Please run this script from the Guardian Node directory"
  exit 1
fi

echo ""
echo "All checks passed! Your Raspberry Pi 5 is ready for Guardian Node."
echo "To build and run the Docker container, run:"
echo "  ./scripts/build_docker_pi5.sh"