---
inclusion: always
---

# Guardian Node Product Guidelines

Guardian Node is an offline AI cybersecurity appliance with strict privacy-first principles. When working on this codebase, adhere to these product requirements:

## Architecture Constraints
- **Zero External Dependencies**: Never implement cloud APIs, telemetry, or external service calls
- **Offline-Only Operation**: All functionality must work without internet connectivity
- **Local Data Storage**: All user data, logs, and configurations remain on device
- **Hardware Target**: Raspberry Pi 5 with touchscreen interface

## Core Components
- **Guardian Interpreter**: Python-based AI agent framework (main application logic)
- **Skill System**: Modular cybersecurity functions with standardized interfaces
- **Local LLM**: GGUF model integration via llama-cpp-python
- **Security Engine**: Network scanning, threat detection, password auditing

## Development Principles
- **Security by Default**: Implement fail-safe mechanisms, validate all inputs
- **Privacy Protection**: No data collection, comprehensive audit logging for transparency
- **Modular Design**: Skills must be self-contained and easily extensible
- **Resource Efficiency**: Optimize for limited Pi 5 hardware resources

## User Experience Requirements
- **Non-Technical Users**: Interface must be intuitive for families and small businesses
- **High-Risk Users**: Support journalists, activists requiring maximum privacy
- **Offline Workflow**: All features accessible without network connectivity
- **Educational Focus**: Provide cybersecurity coaching and explanations

## Technical Standards
- Use Python for core logic with type hints and comprehensive error handling
- Implement standardized skill interfaces for extensibility
- Maintain detailed logging for security auditing
- Follow defensive programming practices for untrusted input