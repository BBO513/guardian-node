#!/bin/bash
# Installation script for Guardian Node

set -e  # Exit on error

echo "Guardian Node Installation"
echo "=========================="

# Check Python version
echo -n "Checking Python version... "
if command -v python3 &> /dev/null; then
  PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
  echo "✅ Python $PYTHON_VERSION detected"
else
  echo "❌ Python 3 not found"
  echo "Please install Python 3.8 or higher"
  exit 1
fi

# Create virtual environment
echo -n "Creating virtual environment... "
if [ -d "venv" ]; then
  echo "✅ Virtual environment already exists"
else
  python3 -m venv venv
  echo "✅ Created virtual environment"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p models logs data

# Check for GGUF model
echo -n "Checking for GGUF model... "
if [ -f "models/Phi-3-mini-4k-instruct-q4.gguf" ]; then
  echo "✅ Phi-3 model found"
else
  echo "❌ Phi-3 model not found"
  echo "Please download the Phi-3 model and place it in the models directory:"
  echo "models/Phi-3-mini-4k-instruct-q4.gguf"
fi

# Set up pre-commit hook
echo "Setting up pre-commit hook..."
mkdir -p .git/hooks
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/sh

if git diff --cached --name-only | xargs grep -E '<<<<<<< |=======|>>>>>>> '; then
  echo "Error: Merge conflict markers detected!" >&2
  exit 1
fi
EOF
chmod +x .git/hooks/pre-commit

echo ""
echo "Installation complete!"
echo ""
echo "To run Guardian Node:"
echo "  source venv/bin/activate"
echo "  python3 guardian_interpreter/main.py"
echo ""
echo "For GUI mode:"
echo "  python3 guardian_interpreter/main.py --gui --mcp --family-mode"
echo ""
echo "For Docker deployment:"
echo "  docker-compose up -d"