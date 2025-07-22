---
inclusion: always
---

# Guardian Interpreter Technical Guidelines

## Core Architecture

### Modular Skills System
- Each skill is a standalone Python module in the `skills/` directory
- Skills must implement a `run()` function as the entry point
- Skills should be self-contained with minimal external dependencies
- Use descriptive skill names that reflect their functionality

### Configuration Management
- All behavior is controlled via `config.yaml` in the root directory
- Configuration changes should not require code modifications
- Use YAML best practices: consistent indentation, clear key names
- Validate configuration on startup and provide clear error messages

### Privacy and Security
- Implement comprehensive audit logging for all operations
- Log security events separately from general application logs
- Block unauthorized network requests by default
- Never log sensitive data (API keys, personal information)

## Code Style and Conventions

### Python Standards
- Target Python 3.8+ compatibility
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Include docstrings for all public functions and classes

### Error Handling
- Use specific exception types rather than generic `Exception`
- Provide meaningful error messages to users
- Log errors with sufficient context for debugging
- Gracefully handle missing dependencies or configuration

### File Organization
```
guardian_interpreter/
├── main.py              # Entry point
├── config.yaml          # Configuration file
├── skills/              # Modular skills directory
│   ├── __init__.py
│   └── skill_name.py    # Individual skill modules
└── logs/                # Application and audit logs
```

## Dependencies and Requirements

### Core Dependencies
- `pyyaml>=6.0`: Configuration parsing
- `psutil>=5.8.0`: System monitoring
- `llama-cpp-python>=0.2.0`: Local LLM inference
- `requests>=2.25.0`: HTTP requests (online mode only)

### Hardware Considerations
- Primary target: Raspberry Pi 5 (16GB RAM)
- Minimum requirements: 4GB RAM, 10GB storage
- Optimize for resource-constrained environments
- Use GGUF model format for efficient local inference

## Development Guidelines

### Testing and Debugging
- Use `config.yaml` to enable debug logging
- Monitor both `logs/guardian.log` and `logs/audit.log`
- Test skills individually before integration
- Validate configuration changes thoroughly

### Local LLM Integration
- Use llama-cpp-python for local model inference
- Support GGUF model format exclusively
- Implement proper model loading error handling
- Provide clear feedback on model compatibility issues