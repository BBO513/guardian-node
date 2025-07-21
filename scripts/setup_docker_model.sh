#!/bin/bash

# Guardian Node - Docker Model Runner Setup Script
# This script helps set up the Docker Model Runner for offline LLM inference

set -e

echo "🛡️  Guardian Node - Docker Model Runner Setup"
echo "=============================================="

# Configuration
MODEL_NAME="guardian-node-llm"
MODEL_VERSION="v1"
MODEL_REGISTRY="localhost:5000"
MODEL_PORT="8080"
MODELS_DIR="./models"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed and running
check_docker() {
    print_status "Checking Docker installation..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    print_success "Docker is installed and running"
}

# Check for GGUF model files
check_models() {
    print_status "Checking for GGUF model files..."
    
    if [ ! -d "$MODELS_DIR" ]; then
        mkdir -p "$MODELS_DIR"
        print_warning "Created models directory: $MODELS_DIR"
    fi
    
    GGUF_FILES=$(find "$MODELS_DIR" -name "*.gguf" 2>/dev/null || true)
    
    if [ -z "$GGUF_FILES" ]; then
        print_warning "No GGUF model files found in $MODELS_DIR"
        echo "Please download a compatible GGUF model file to the models directory."
        echo "Recommended models:"
        echo "  - Phi-3-mini-4k-instruct (Q4_K_M)"
        echo "  - Llama-3.2-3B-Instruct (Q4_K_M)"
        echo "  - Qwen2.5-3B-Instruct (Q4_K_M)"
        echo ""
        echo "You can continue with the setup and add models later."
        read -p "Continue without models? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        print_success "Found GGUF model files:"
        echo "$GGUF_FILES"
    fi
}

# Package a GGUF model with Docker Model Runner
package_model() {
    local model_file="$1"
    local license_file="$2"
    
    if [ ! -f "$model_file" ]; then
        print_error "Model file not found: $model_file"
        return 1
    fi
    
    print_status "Packaging model: $(basename "$model_file")"
    
    # Build the docker model package command
    DOCKER_CMD="docker model package --gguf \"$model_file\""
    
    if [ -f "$license_file" ]; then
        DOCKER_CMD="$DOCKER_CMD --license \"$license_file\""
    fi
    
    DOCKER_CMD="$DOCKER_CMD --push $MODEL_REGISTRY/$MODEL_NAME:$MODEL_VERSION"
    
    print_status "Running: $DOCKER_CMD"
    
    if eval "$DOCKER_CMD"; then
        print_success "Model packaged successfully: $MODEL_REGISTRY/$MODEL_NAME:$MODEL_VERSION"
        return 0
    else
        print_error "Failed to package model"
        return 1
    fi
}

# Start the model server
start_model_server() {
    print_status "Starting Docker Model Runner server..."
    
    # Stop any existing container
    docker stop guardian-llm-server 2>/dev/null || true
    docker rm guardian-llm-server 2>/dev/null || true
    
    # Start the model server
    if docker model run "$MODEL_REGISTRY/$MODEL_NAME:$MODEL_VERSION" \
        --name guardian-llm-server \
        --port "$MODEL_PORT" \
        --detach; then
        print_success "Model server started on port $MODEL_PORT"
        
        # Wait for server to be ready
        print_status "Waiting for server to be ready..."
        for i in {1..30}; do
            if curl -s "http://localhost:$MODEL_PORT/health" >/dev/null 2>&1; then
                print_success "Server is ready!"
                break
            fi
            sleep 2
            echo -n "."
        done
        echo
        
    else
        print_error "Failed to start model server"
        return 1
    fi
}

# Test the model API
test_model_api() {
    print_status "Testing model API..."
    
    local test_response
    test_response=$(curl -s -X POST "http://localhost:$MODEL_PORT/v1/chat/completions" \
        -H "Content-Type: application/json" \
        -d '{
            "messages": [
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": "Hello, are you running offline?"}
            ],
            "max_tokens": 100,
            "temperature": 0.7
        }' 2>/dev/null || echo "ERROR")
    
    if [ "$test_response" = "ERROR" ]; then
        print_error "Failed to connect to model API"
        return 1
    fi
    
    if echo "$test_response" | grep -q "choices"; then
        print_success "Model API is working correctly!"
        echo "Test response:"
        echo "$test_response" | python3 -m json.tool 2>/dev/null || echo "$test_response"
    else
        print_warning "Model API responded but format may be unexpected"
        echo "Response: $test_response"
    fi
}

# Main setup function
main() {
    echo "Starting Guardian Node Docker Model Runner setup..."
    echo
    
    check_docker
    check_models
    
    # Interactive model selection and packaging
    if [ -n "$GGUF_FILES" ]; then
        echo
        echo "Available GGUF models:"
        select model_file in $GGUF_FILES "Skip packaging"; do
            case $model_file in
                "Skip packaging")
                    print_status "Skipping model packaging"
                    break
                    ;;
                *)
                    if [ -n "$model_file" ]; then
                        # Look for license file
                        model_dir=$(dirname "$model_file")
                        license_file=""
                        for license in "$model_dir/LICENSE" "$model_dir/LICENSE.txt" "$model_dir/license.txt"; do
                            if [ -f "$license" ]; then
                                license_file="$license"
                                break
                            fi
                        done
                        
                        if package_model "$model_file" "$license_file"; then
                            break
                        else
                            print_error "Failed to package model, please try again"
                        fi
                    else
                        print_error "Invalid selection"
                    fi
                    ;;
            esac
        done
    fi
    
    # Ask if user wants to start the server
    echo
    read -p "Start the model server now? (Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        print_status "Skipping server startup"
        echo "You can start the server later with:"
        echo "  docker model run $MODEL_REGISTRY/$MODEL_NAME:$MODEL_VERSION --port $MODEL_PORT"
    else
        start_model_server
        test_model_api
    fi
    
    echo
    print_success "Setup complete!"
    echo
    echo "Next steps:"
    echo "1. Update your Guardian config.yaml to use Docker Model Runner"
    echo "2. Start Guardian Node with: docker-compose up"
    echo "3. The LLM will automatically connect to the Docker Model Runner"
    echo
    echo "Useful commands:"
    echo "  - Check server status: curl http://localhost:$MODEL_PORT/health"
    echo "  - View server logs: docker logs guardian-llm-server"
    echo "  - Stop server: docker stop guardian-llm-server"
}

# Run main function
main "$@"