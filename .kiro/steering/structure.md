---
inclusion: always
---

# Guardian Node Project Structure

## Architecture Overview
Guardian Node is a local modular AI agent system with two main components:
- **guardian_interpreter**: Full-featured application with security controls
- **guardian_interpreter_starter**: Simplified version for development/testing

## Directory Structure
```
guardian-node/
├── guardian_interpreter/          # Main secure AI agent
├── guardian_interpreter_starter/  # Development/testing version
├── README.md                      # Project documentation
└── Guardian Interpreter – Local Modular AI Agent (Nodie Edition).md
```

### Core Application Structure
```
guardian_interpreter/
├── main.py                 # CLI entry point and orchestration
├── config.yaml            # Central configuration
├── llm_integration.py      # Local LLM interface
├── network_security.py     # Security enforcement layer
├── requirements.txt        # Python dependencies
├── install.sh             # Setup automation
├── skills/                # Modular capability system
│   ├── __init__.py
│   ├── example_skill.py    # Development template
│   ├── lan_scanner.py      # Network discovery
│   ├── router_checker.py   # Security assessment
│   └── system_info.py      # System diagnostics
└── logs/                  # Runtime logging (auto-created)
    ├── guardian.log        # Application events
    ├── blocked_calls.log   # Security violations
    └── audit.log          # Complete activity trail
```

## Development Conventions

### Skills Architecture
- **Location**: All skills in `skills/` directory as standalone Python modules
- **Entry Point**: Required `run(*args, **kwargs)` function
- **Documentation**: Include module docstring describing functionality
- **Metadata**: Optional `__version__`, `__author__` attributes
- **Error Handling**: Skills must handle exceptions gracefully
- **Return Values**: Consistent return format (dict with status/data)

### Configuration Management
- **Single Source**: All settings in `config.yaml`
- **Sections**:
  - `network:` - Security and connectivity settings
  - `llm:` - Model configuration and parameters
  - `logging:` - Log levels and destinations
  - `skills:` - Skill-specific configurations
- **Environment Override**: Support for environment variable overrides

### Security Model
- **Default Posture**: Internet access disabled (`ALLOW_ONLINE: false`)
- **Audit Trail**: All network attempts logged to `blocked_calls.log`
- **Privacy First**: No telemetry, analytics, or external API calls
- **Local Only**: All processing happens on local machine
- **Transparent Logging**: Complete audit trail in `audit.log`

### Code Style Guidelines
- **File Naming**: Snake_case for Python modules (`network_security.py`)
- **Function Naming**: Snake_case for functions and variables
- **Class Naming**: PascalCase for classes
- **Constants**: UPPER_CASE for configuration constants
- **Imports**: Standard library first, then third-party, then local imports
- **Documentation**: Docstrings for all public functions and classes

### Logging Standards
- **Structured Logging**: Use consistent log format across modules
- **Log Levels**: DEBUG for development, INFO for operations, ERROR for issues
- **File Separation**:
  - `guardian.log`: Application flow and user interactions
  - `blocked_calls.log`: Security events and blocked operations
  - `audit.log`: Complete system activity for compliance
- **Rotation**: Implement log rotation for production deployments

### Error Handling
- **Graceful Degradation**: System continues operating when skills fail
- **User Feedback**: Clear error messages for user-facing issues
- **Logging**: All errors logged with context and stack traces
- **Recovery**: Automatic retry for transient failures where appropriate