#!/bin/bash
set -e

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

echo "Setup complete. Copy microsoft_Phi-4-mini-instruct-Q4_K_M.gguf to models/ manually."