#!/bin/bash
# Guardian Interpreter Installation Script
# Owner: Blackbox Matrix

echo "Guardian Interpreter Installation"
echo "================================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✓ Python $python_version detected (>= 3.8 required)"
else
    echo "✗ Python 3.8+ required. Current version: $python_version"
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "✗ pip3 not found. Please install pip3 first."
    exit 1
fi

echo "✓ pip3 available"

# Install dependencies
echo ""
echo "Installing Python dependencies..."
echo "================================"

if pip3 install -r requirements.txt; then
    echo "✓ Dependencies installed successfully"
else
    echo "✗ Failed to install dependencies"
    echo "Try installing manually:"
    echo "  pip3 install pyyaml psutil requests llama-cpp-python"
    exit 1
fi

# Create directories if they don't exist
echo ""
echo "Setting up directories..."
mkdir -p models logs
echo "✓ Directories created"

# Set permissions
chmod +x main.py
echo "✓ Permissions set"

# Check if model exists
echo ""
echo "Checking for LLM model..."
if [ -f "models/your-model.gguf" ]; then
    echo "✓ Model file found"
else
    echo "⚠️  No model file found at models/your-model.gguf"
    echo "   Download a GGUF model and place it in the models/ directory"
    echo "   Update the model_path in config.yaml accordingly"
fi

echo ""
echo "Installation Complete!"
echo "====================="
echo ""
echo "To start Guardian Interpreter:"
echo "  python3 main.py"
echo ""
echo "For help and documentation:"
echo "  cat README.md"
echo ""
echo "Privacy Notice:"
echo "- All network requests are BLOCKED by default"
echo "- No telemetry or external data collection"
echo "- All actions are logged locally for audit"
echo ""

