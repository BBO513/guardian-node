#!/bin/bash
# Script to download the Phi-3-mini-4k-instruct-q4.gguf model

set -e

# Create models directory if it doesn't exist
mkdir -p models

# Model URL
MODEL_URL="https://huggingface.co/microsoft/phi-3-mini-4k-instruct/resolve/main/phi-3-mini-4k-instruct-q4.gguf"
MODEL_PATH="models/phi-3-mini-4k-instruct-q4.gguf"

echo "Downloading Phi-3-mini-4k-instruct-q4.gguf model..."
echo "This may take a while depending on your internet connection."

# Check if wget is available
if command -v wget &> /dev/null; then
    wget -O "$MODEL_PATH" "$MODEL_URL"
# Check if curl is available
elif command -v curl &> /dev/null; then
    curl -L "$MODEL_URL" -o "$MODEL_PATH"
else
    echo "Error: Neither wget nor curl is available. Please install one of them and try again."
    exit 1
fi

echo "Model downloaded successfully to $MODEL_PATH"
echo "Update config.yaml to use this model path."