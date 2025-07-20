# Project Structure

## Repository Layout
```
guardian-node/
├── guardian_interpreter/          # Main application
├── guardian_interpreter_starter/  # Simplified starter version
├── README.md                      # Project overview
├── Guardian Interpreter – Local Modular AI Agent (Nodie Edition).md
└── image_offline_ai.png          # Concept image
```

## Guardian Interpreter Structure
```
guardian_interpreter/
├── main.py                 # Application entry point and CLI
├── config.yaml            # Main configuration file
├── llm_integration.py      # Local LLM handling
├── network_security.py     # Security and audit logging
├── requirements.txt        # Python dependencies
├── install.sh             # Installation script
├── README.md              # Module documentation
├── skills/                # Modular skill system
│   ├── __init__.py
│   ├── example_skill.py    # Skill template
│   ├── lan_scanner.py      # Network scanning
│   ├── router_checker.py   # Router security
│   └── system_info.py      # System information
└── logs/                  # Log files (created at runtime)
    ├── guardian.log        # Main application log
    ├── blocked_calls.log   # Network security log
    └── audit.log          # Comprehensive audit trail
```

## Key Conventions

### Skills Development
- Each skill is a standalone `.py` file in `skills/` directory
- Must have a `run(*args, **kwargs)` function as entry point
- Should include docstring with description
- Optional metadata: `__doc__`, `__version__`, `__author__`

### Configuration
- All configuration in `config.yaml`
- Network security settings under `network:` section
- LLM settings under `llm:` section
- Logging configuration under `logging:` section

### Logging Structure
- Main application events → `logs/guardian.log`
- Blocked network requests → `logs/blocked_calls.log`
- Comprehensive audit trail → `logs/audit.log`
- All user actions and system events are logged

### Security Principles
- Internet access blocked by default (`ALLOW_ONLINE: false`)
- All network attempts logged and audited
- No telemetry or external API calls
- Privacy-first design throughout

### File Naming
- Core modules: lowercase with underscores (`network_security.py`)
- Skills: descriptive names (`lan_scanner.py`, `router_checker.py`)
- Config files: `config.yaml` (consistent naming)
- Log files: descriptive with `.log` extension