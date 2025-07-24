#!/bin/bash
set -e

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

echo "Setup complete. Copy Phi-3-mini-4k-instruct-q4.gguf to models/ manually."