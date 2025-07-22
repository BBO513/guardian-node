#!/bin/bash
set -e

# Guardian Node Docker Entrypoint Script
# Handles initialization and startup for containerized deployment

echo "🛡️  Guardian Node Container Starting..."
echo "=================================="

# Environment variables with defaults
GUARDIAN_MODE=${GUARDIAN_MODE:-family}
GUARDIAN_OFFLINE=${GUARDIAN_OFFLINE:-true}
GUARDIAN_GUI_ENABLED=${GUARDIAN_GUI_ENABLED:-false}
GUARDIAN_FAMILY_MODE=${GUARDIAN_FAMILY_MODE:-true}
GUARDIAN_DATA_PATH=${GUARDIAN_DATA_PATH:-/data}
GUARDIAN_LOGS_PATH=${GUARDIAN_LOGS_PATH:-/logs}

echo "Configuration:"
echo "  Mode: $GUARDIAN_MODE"
echo "  Offline: $GUARDIAN_OFFLINE"
echo "  GUI Enabled: $GUARDIAN_GUI_ENABLED"
echo "  Family Mode: $GUARDIAN_FAMILY_MODE"
echo "  Data Path: $GUARDIAN_DATA_PATH"
echo "  Logs Path: $GUARDIAN_LOGS_PATH"

# Create necessary directories
echo "Creating directories..."
mkdir -p "$GUARDIAN_DATA_PATH"
mkdir -p "$GUARDIAN_LOGS_PATH"
mkdir -p /app/models
mkdir -p /app/config

# Set proper permissions
echo "Setting permissions..."
chown -R guardian:guardian "$GUARDIAN_DATA_PATH"
chown -R guardian:guardian "$GUARDIAN_LOGS_PATH"
chown -R guardian:guardian /app/models
chown -R guardian:guardian /app/config

# Generate default configuration if not exists
CONFIG_FILE="/app/guardian_interpreter/config.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Generating default configuration..."
    cat > "$CONFIG_FILE" << EOF
# Guardian Node Container Configuration
system:
  name: "Guardian Node Family Assistant"
  version: "1.0.0"
  owner: "Guardian Family"

# Network Security (Privacy-First)
network:
  ALLOW_ONLINE: ${GUARDIAN_OFFLINE:-false}
  allowed_domains: []
  log_blocked_calls: true

# Family Assistant Settings
family_assistant:
  enabled: ${GUARDIAN_FAMILY_MODE:-true}
  gui_enabled: ${GUARDIAN_GUI_ENABLED:-false}
  default_interface: "cli"
  family_data_path: "$GUARDIAN_DATA_PATH/families"
  
  # Family-specific LLM settings
  family_llm:
    child_safe_mode: true
    default_safety_level: "standard"
    
  # Voice interface
  voice_interface:
    enabled: false
    privacy_mode: true

# Logging
logging:
  level: "INFO"
  main_log: "$GUARDIAN_LOGS_PATH/guardian.log"
  blocked_calls_log: "$GUARDIAN_LOGS_PATH/blocked_calls.log"
  max_log_size_mb: 10

# CLI Settings
cli:
  prompt_prefix: "Guardian> "
  show_skill_list_on_start: true

# LLM Configuration
llm:
  model_path: "/app/models/your-model.gguf"
  context_length: 4096
  temperature: 0.7
  max_tokens: 512
  threads: 4
EOF
fi

# Check for LLM model
MODEL_PATH="/app/models"
if [ -d "$MODEL_PATH" ] && [ "$(ls -A $MODEL_PATH)" ]; then
    echo "✓ LLM models found in $MODEL_PATH"
    ls -la "$MODEL_PATH"
else
    echo "⚠️  No LLM models found in $MODEL_PATH"
    echo "   Add GGUF model files to enable AI functionality"
fi

# Health check setup
echo "Setting up health monitoring..."
cat > /app/health_status.json << EOF
{
    "status": "starting",
    "timestamp": "$(date -Iseconds)",
    "mode": "$GUARDIAN_MODE",
    "offline": $GUARDIAN_OFFLINE,
    "family_mode": $GUARDIAN_FAMILY_MODE
}
EOF

# Function to handle shutdown gracefully
shutdown_handler() {
    echo "🛑 Received shutdown signal..."
    echo "Performing graceful shutdown..."
    
    # Update health status
    cat > /app/health_status.json << EOF
{
    "status": "shutting_down",
    "timestamp": "$(date -Iseconds)",
    "mode": "$GUARDIAN_MODE"
}
EOF
    
    # Kill background processes
    if [ ! -z "$GUARDIAN_PID" ]; then
        echo "Stopping Guardian Node (PID: $GUARDIAN_PID)..."
        kill -TERM "$GUARDIAN_PID" 2>/dev/null || true
        wait "$GUARDIAN_PID" 2>/dev/null || true
    fi
    
    echo "✓ Guardian Node stopped gracefully"
    exit 0
}

# Set up signal handlers
trap shutdown_handler SIGTERM SIGINT

# Start Guardian Node based on mode
echo "=================================="
echo "🚀 Starting Guardian Node..."

cd /app/guardian_interpreter

# Update health status
cat > /app/health_status.json << EOF
{
    "status": "running",
    "timestamp": "$(date -Iseconds)",
    "mode": "$GUARDIAN_MODE",
    "offline": $GUARDIAN_OFFLINE,
    "family_mode": $GUARDIAN_FAMILY_MODE,
    "pid": "$$"
}
EOF

# Determine startup command based on mode and arguments
if [ "$#" -eq 0 ] || [ "$1" = "python" ]; then
    # Default: Start Guardian Node
    if [ "$GUARDIAN_GUI_ENABLED" = "true" ]; then
        echo "Starting Guardian Node with GUI..."
        exec python main.py --gui &
    else
        echo "Starting Guardian Node in CLI mode..."
        exec python main.py &
    fi
    GUARDIAN_PID=$!
    
elif [ "$1" = "family-cli" ]; then
    # Start Family Assistant CLI
    echo "Starting Guardian Family Assistant CLI..."
    exec python -c "
import sys
sys.path.append('/app')
from guardian_family_cli_enhanced import main
main()
    " &
    GUARDIAN_PID=$!
    
elif [ "$1" = "test" ]; then
    # Run tests
    echo "Running Guardian Node tests..."
    cd /app
    exec python test_guardian_integration.py
    
elif [ "$1" = "bash" ] || [ "$1" = "sh" ]; then
    # Interactive shell
    echo "Starting interactive shell..."
    exec /bin/bash
    
else
    # Custom command
    echo "Executing custom command: $@"
    exec "$@" &
    GUARDIAN_PID=$!
fi

# Wait for the main process
if [ ! -z "$GUARDIAN_PID" ]; then
    echo "Guardian Node started with PID: $GUARDIAN_PID"
    echo "✓ Guardian Node is running"
    echo "=================================="
    
    # Wait for the process to finish
    wait "$GUARDIAN_PID"
    EXIT_CODE=$?
    
    echo "Guardian Node exited with code: $EXIT_CODE"
    
    # Update health status
    cat > /app/health_status.json << EOF
{
    "status": "stopped",
    "timestamp": "$(date -Iseconds)",
    "exit_code": $EXIT_CODE
}
EOF
    
    exit $EXIT_CODE
fi