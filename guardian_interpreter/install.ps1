# Guardian Interpreter Installation Script for Windows
# PowerShell script to set up the environment

# Exit on error
$ErrorActionPreference = "Stop"

# Create virtual environment if it doesn't exist
if (-not (Test-Path -Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..."
& .\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..."
pip install -r requirements.txt

Write-Host "Setup complete. Copy Phi-3-mini-4k-instruct-q4.gguf to models\ manually."