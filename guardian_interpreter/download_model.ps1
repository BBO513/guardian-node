# Script to download the microsoft_Phi-4-mini-instruct-Q4_K_M.gguf model
# PowerShell version

# Create models directory if it doesn't exist
if (-not (Test-Path -Path "models")) {
    New-Item -ItemType Directory -Path "models"
}

# Model URL
$MODEL_URL = "https://huggingface.co/bartowski/microsoft_Phi-4-mini-instruct-GGUF/resolve/main/microsoft_Phi-4-mini-instruct-Q4_K_M.gguf"
$MODEL_PATH = "models/microsoft_Phi-4-mini-instruct-Q4_K_M.gguf"

Write-Host "Downloading microsoft_Phi-4-mini-instruct-Q4_K_M.gguf model..."
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