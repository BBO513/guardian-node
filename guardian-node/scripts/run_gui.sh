#!/bin/bash
# Script to run Guardian Node with GUI interface
# Optimized for 4.5-inch Raspberry Pi touchscreen

echo "Starting Guardian Node with GUI interface..."
echo "============================================"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
  echo "Activating virtual environment..."
  source venv/bin/activate
fi

# Check if Phi-3 model exists
MODEL_PATH="models/Phi-3-mini-4k-instruct-q4.gguf"
if [ ! -f "$MODEL_PATH" ]; then
  echo "Warning: Phi-3 model not found at $MODEL_PATH"
  echo "Guardian Node will use the default model or prompt for a model path."
fi

# Run Guardian Node with GUI, MCP, and family mode
echo "Launching Guardian Node GUI..."
python3 guardian_interpreter/main.py --gui --mcp --family-mode

# Handle exit
echo "Guardian Node GUI has been closed."