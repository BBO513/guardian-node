# Technology Stack

## Core Technologies
- **Python 3.8+**: Primary programming language
- **YAML**: Configuration management
- **GGUF Models**: Local LLM model format
- **llama-cpp-python**: Local LLM inference engine

## Key Dependencies
- `pyyaml>=6.0`: Configuration file parsing
- `psutil>=5.8.0`: System information and monitoring
- `requests>=2.25.0`: HTTP requests (when online mode enabled)
- `llama-cpp-python>=0.2.0`: Local LLM inference
- `ipaddress>=1.0.23`: Network utilities

## Architecture Patterns
- **Modular Skills System**: Each skill is a standalone Python module with a `run()` function
- **Configuration-Driven**: All behavior controlled via `config.yaml`
- **Privacy-First Logging**: Comprehensive audit trails with security event tracking
- **Network Security Layer**: Built-in request blocking and monitoring

## Common Commands

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Install with specific LLM support
pip install llama-cpp-python pyyaml psutil requests
```

### Running
```bash
# Start Guardian Interpreter
python main.py

# Run with specific config
python main.py --config custom_config.yaml
```

### Development
```bash
# Check logs
tail -f logs/guardian.log
tail -f logs/audit.log

# Debug mode (set in config.yaml)
logging:
  level: "DEBUG"
```

## Hardware Targets
- **Primary**: Raspberry Pi 5 (16GB RAM)
- **Secondary**: Standard PC/Linux systems
- **Requirements**: 4GB+ RAM, 10GB+ storage