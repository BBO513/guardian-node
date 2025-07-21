# Guardian Node - Docker Model Runner Setup Script (PowerShell)
# This script helps set up the Docker Model Runner for offline LLM inference

param(
    [string]$ModelName = "guardian-node-llm",
    [string]$ModelVersion = "v1",
    [string]$ModelRegistry = "localhost:5000",
    [int]$ModelPort = 8080,
    [string]$ModelsDir = "./models"
)

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Cyan"

function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor $Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor $Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $Red
}

function Test-Docker {
    Write-Status "Checking Docker installation..."
    
    try {
        $null = Get-Command docker -ErrorAction Stop
        $null = docker info 2>$null
        Write-Success "Docker is installed and running"
        return $true
    }
    catch {
        Write-Error "Docker is not installed or not running. Please install and start Docker first."
        return $false
    }
}

function Test-Models {
    Write-Status "Checking for GGUF model files..."
    
    if (!(Test-Path $ModelsDir)) {
        New-Item -ItemType Directory -Path $ModelsDir -Force | Out-Null
        Write-Warning "Created models directory: $ModelsDir"
    }
    
    $ggufFiles = Get-ChildItem -Path $ModelsDir -Filter "*.gguf" -ErrorAction SilentlyContinue
    
    if ($ggufFiles.Count -eq 0) {
        Write-Warning "No GGUF model files found in $ModelsDir"
        Write-Host "Please download a compatible GGUF model file to the models directory."
        Write-Host "Recommended models:"
        Write-Host "  - Phi-3-mini-4k-instruct (Q4_K_M)"
        Write-Host "  - Llama-3.2-3B-Instruct (Q4_K_M)"
        Write-Host "  - Qwen2.5-3B-Instruct (Q4_K_M)"
        Write-Host ""
        
        $continue = Read-Host "Continue without models? (y/N)"
        if ($continue -ne "y" -and $continue -ne "Y") {
            exit 1
        }
        return @()
    }
    else {
        Write-Success "Found GGUF model files:"
        $ggufFiles | ForEach-Object { Write-Host "  - $($_.Name)" }
        return $ggufFiles
    }
}

function Invoke-PackageModel {
    param(
        [string]$ModelFile,
        [string]$LicenseFile = ""
    )
    
    if (!(Test-Path $ModelFile)) {
        Write-Error "Model file not found: $ModelFile"
        return $false
    }
    
    Write-Status "Packaging model: $(Split-Path $ModelFile -Leaf)"
    
    # Build the docker model package command
    $dockerCmd = "docker model package --gguf `"$ModelFile`""
    
    if ($LicenseFile -and (Test-Path $LicenseFile)) {
        $dockerCmd += " --license `"$LicenseFile`""
    }
    
    $dockerCmd += " --push $ModelRegistry/$ModelName`:$ModelVersion"
    
    Write-Status "Running: $dockerCmd"
    
    try {
        Invoke-Expression $dockerCmd
        Write-Success "Model packaged successfully: $ModelRegistry/$ModelName`:$ModelVersion"
        return $true
    }
    catch {
        Write-Error "Failed to package model: $($_.Exception.Message)"
        return $false
    }
}

function Start-ModelServer {
    Write-Status "Starting Docker Model Runner server..."
    
    # Stop any existing container
    try {
        docker stop guardian-llm-server 2>$null | Out-Null
        docker rm guardian-llm-server 2>$null | Out-Null
    }
    catch {
        # Ignore errors if container doesn't exist
    }
    
    # Start the model server
    try {
        $dockerCmd = "docker model run $ModelRegistry/$ModelName`:$ModelVersion --name guardian-llm-server --port $ModelPort --detach"
        Invoke-Expression $dockerCmd
        Write-Success "Model server started on port $ModelPort"
        
        # Wait for server to be ready
        Write-Status "Waiting for server to be ready..."
        for ($i = 1; $i -le 30; $i++) {
            try {
                $response = Invoke-WebRequest -Uri "http://localhost:$ModelPort/health" -TimeoutSec 2 -ErrorAction Stop
                if ($response.StatusCode -eq 200) {
                    Write-Success "Server is ready!"
                    return $true
                }
            }
            catch {
                # Continue waiting
            }
            Start-Sleep -Seconds 2
            Write-Host "." -NoNewline
        }
        Write-Host ""
        Write-Warning "Server may still be starting up"
        return $true
    }
    catch {
        Write-Error "Failed to start model server: $($_.Exception.Message)"
        return $false
    }
}

function Test-ModelAPI {
    Write-Status "Testing model API..."
    
    try {
        $body = @{
            messages = @(
                @{ role = "system"; content = "You are a helpful AI assistant." },
                @{ role = "user"; content = "Hello, are you running offline?" }
            )
            max_tokens = 100
            temperature = 0.7
        } | ConvertTo-Json -Depth 3
        
        $response = Invoke-RestMethod -Uri "http://localhost:$ModelPort/v1/chat/completions" `
            -Method Post `
            -ContentType "application/json" `
            -Body $body `
            -TimeoutSec 30
        
        if ($response.choices) {
            Write-Success "Model API is working correctly!"
            Write-Host "Test response:"
            $response | ConvertTo-Json -Depth 3 | Write-Host
        }
        else {
            Write-Warning "Model API responded but format may be unexpected"
            Write-Host "Response: $($response | ConvertTo-Json)"
        }
        return $true
    }
    catch {
        Write-Error "Failed to test model API: $($_.Exception.Message)"
        return $false
    }
}

# Main execution
Write-Host "🛡️  Guardian Node - Docker Model Runner Setup" -ForegroundColor $Blue
Write-Host "=============================================="
Write-Host ""

if (!(Test-Docker)) {
    exit 1
}

$ggufFiles = Test-Models

# Interactive model selection and packaging
if ($ggufFiles.Count -gt 0) {
    Write-Host ""
    Write-Host "Available GGUF models:"
    for ($i = 0; $i -lt $ggufFiles.Count; $i++) {
        Write-Host "  $($i + 1). $($ggufFiles[$i].Name)"
    }
    Write-Host "  $($ggufFiles.Count + 1). Skip packaging"
    
    do {
        $selection = Read-Host "Select a model to package (1-$($ggufFiles.Count + 1))"
        $selectionNum = [int]$selection
    } while ($selectionNum -lt 1 -or $selectionNum -gt ($ggufFiles.Count + 1))
    
    if ($selectionNum -le $ggufFiles.Count) {
        $selectedModel = $ggufFiles[$selectionNum - 1]
        $modelFile = $selectedModel.FullName
        
        # Look for license file
        $licenseFile = ""
        $modelDir = Split-Path $modelFile -Parent
        $licenseFiles = @("LICENSE", "LICENSE.txt", "license.txt")
        foreach ($license in $licenseFiles) {
            $licensePath = Join-Path $modelDir $license
            if (Test-Path $licensePath) {
                $licenseFile = $licensePath
                break
            }
        }
        
        if (!(Invoke-PackageModel -ModelFile $modelFile -LicenseFile $licenseFile)) {
            Write-Error "Failed to package model"
            exit 1
        }
    }
    else {
        Write-Status "Skipping model packaging"
    }
}

# Ask if user wants to start the server
Write-Host ""
$startServer = Read-Host "Start the model server now? (Y/n)"
if ($startServer -eq "n" -or $startServer -eq "N") {
    Write-Status "Skipping server startup"
    Write-Host "You can start the server later with:"
    Write-Host "  docker model run $ModelRegistry/$ModelName`:$ModelVersion --port $ModelPort"
}
else {
    if (Start-ModelServer) {
        Test-ModelAPI | Out-Null
    }
}

Write-Host ""
Write-Success "Setup complete!"
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Update your Guardian config.yaml to use Docker Model Runner"
Write-Host "2. Start Guardian Node with: docker-compose up"
Write-Host "3. The LLM will automatically connect to the Docker Model Runner"
Write-Host ""
Write-Host "Useful commands:"
Write-Host "  - Check server status: Invoke-WebRequest http://localhost:$ModelPort/health"
Write-Host "  - View server logs: docker logs guardian-llm-server"
Write-Host "  - Stop server: docker stop guardian-llm-server"