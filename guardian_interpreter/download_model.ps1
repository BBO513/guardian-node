# Script to download the Phi-3-mini-4k-instruct-q4.gguf model
# PowerShell version

# Create models directory if it doesn't exist
if (-not (Test-Path -Path "models")) {
    New-Item -ItemType Directory -Path "models"
}

# Model URL
$MODEL_URL = "https://huggingface.co/microsoft/phi-3-mini-4k-instruct/resolve/main/phi-3-mini-4k-instruct-q4.gguf"
$MODEL_PATH = "models/phi-3-mini-4k-instruct-q4.gguf"

Write-Host "Downloading Phi-3-mini-4k-instruct-q4.gguf model..."
Write-Host "This may take a while depending on your internet connection."

try {
    # Use Invoke-WebRequest to download the file
    Invoke-WebRequest -Uri $MODEL_URL -OutFile $MODEL_PATH
    
    Write-Host "Model downloaded successfully to $MODEL_PATH"
    Write-Host "Update config.yaml to use this model path."
}
catch {
    Write-Host "Error downloading the model: $_"
    exit 1
}