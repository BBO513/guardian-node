# Guardian Node Family AI Assistant

## Overview

Guardian Node is an **offline AI cybersecurity appliance** designed for families, activists, and privacy-conscious users. The core philosophy is "Your Own AI. No Cloud. No Spying."

This repository contains the Guardian Node Family AI Assistant, a specialized version focused on family cybersecurity education, protection, and guidance.

## Key Features

- **100% Offline Operation**: No cloud dependencies, telemetry, or external API calls
- **Family Cybersecurity Assistant**: AI-powered threat detection, phishing protection, and security education
- **Privacy-First Design**: All data stays local, comprehensive audit logging, hard-blocked internet by default
- **Enhanced LLM Integration**: Support for multiple GGUF models with automatic discovery and benchmarking
- **Family-Friendly Responses**: Age-appropriate content filtering and context-aware responses
- **Multiple Interfaces**: CLI, GUI (PySide6), voice interface, and web dashboard
- **Docker Deployment**: Optimized container deployment for Raspberry Pi and standard hardware

## Quick Start

### Prerequisites

- Docker and Docker Compose
- 4GB+ RAM (8GB+ recommended)
- GGUF model files (Phi-3-mini-4k-instruct recommended)

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-org/guardian-node.git
   cd guardian-node
   ```

2. **Download GGUF models**:
   ```bash
   mkdir -p models
   # Download your preferred GGUF model to the models directory
   # Example: Phi-3-mini-4k-instruct-q4.gguf
   ```

3. **Start the container**:
   ```bash
   docker-compose up -d
   ```

4. **Access the GUI**:
   Open your browser to `http://localhost:8080`

### Using with Monitoring

To start with Prometheus monitoring:

```bash
docker-compose --profile monitoring up -d
```

Access the Prometheus dashboard at `http://localhost:9090`

## LLM Integration

Guardian Node features an enhanced LLM integration system with:

1. **Multiple Model Support**: Load and manage multiple GGUF models
2. **Automatic Discovery**: Finds all GGUF models in the models directory
3. **Model Benchmarking**: Evaluates model performance for optimal selection
4. **Context-Aware Switching**: Selects appropriate models based on query context
5. **Family-Safe Responses**: Age-appropriate content filtering and formatting

### Supported Models

The system works best with these models:

- **Phi-3-mini-4k-instruct** (recommended for Raspberry Pi)
- **Llama-3.2-3B-Instruct**
- **Qwen2.5-3B-Instruct**

All models should be in GGUF format, preferably quantized (Q4_K_M) for efficiency.

## Family Assistant Features

The Family AI Assistant provides:

- **Child-Safe Mode**: Age-appropriate content filtering and language
- **Family Profiles**: Personalized security recommendations
- **Device Management**: Security guidance for family devices
- **Threat Education**: Family-friendly explanations of cybersecurity concepts
- **Parental Controls**: Guidance on setting up and managing parental controls

## Docker Configuration

The Docker setup is optimized for both development and production:

- **Environment Variables**: Control model paths, security settings, and performance
- **Volume Mounts**: Easy access to models, data, and logs
- **Resource Limits**: Optimized for Raspberry Pi deployment
- **Health Monitoring**: HTTP-based health checks and Prometheus metrics

See [DOCKER_ENHANCEMENTS.md](DOCKER_ENHANCEMENTS.md) for detailed information.

## Development

### Local Setup

1. **Install dependencies**:
   ```bash
   pip install -r guardian_interpreter/requirements.txt
   ```

2. **Run the application**:
   ```bash
   cd guardian_interpreter
   python main.py --gui
   ```

### Testing

```bash
# Run all tests
pytest

# Test LLM integration
python test_llm_integration.py

# Test family-friendly response generation
python test_family_llm_integration.py

# Test enhanced LLM loader
python test_llm_loader_integration.py
```

## Architecture

Guardian Node follows a modular architecture:

- **LLM Integration**: Local inference with GGUF models
- **Family Assistant**: Age-appropriate cybersecurity guidance
- **Protocol Modules**: Security analysis for home networks
- **Skills System**: Modular cybersecurity capabilities
- **GUI Interface**: Family-friendly touchscreen interface
- **Voice Interface**: Optional speech interaction

## Security Features

- **Offline-by-Default**: No internet connectivity required
- **Data Encryption**: Family data is encrypted at rest
- **Audit Logging**: Comprehensive activity logging
- **Tamper Protection**: Secure audit trail
- **Container Isolation**: Secure Docker deployment

## License

[Insert License Information]

## Acknowledgments

- The Guardian Node Team
- Contributors and testers
- Open source projects that made this possible