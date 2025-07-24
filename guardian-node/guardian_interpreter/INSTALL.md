# Guardian Node Installation Guide

This guide provides instructions for setting up the Guardian Node Family AI Assistant.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (for cloning the repository)

## Installation

### Linux/macOS

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-org/guardian-node.git
   cd guardian-node/guardian_interpreter
   ```

2. **Run the installation script**:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

3. **Download the model** (optional):
   ```bash
   chmod +x download_model.sh
   ./download_model.sh
   ```

4. **Run the application**:
   ```bash
   source venv/bin/activate
   python main.py
   ```

### Windows

1. **Clone the repository**:
   ```powershell
   git clone https://github.com/your-org/guardian-node.git
   cd guardian-node\guardian_interpreter
   ```

2. **Run the installation script**:
   ```powershell
   .\install.ps1
   ```

3. **Download the model** (optional):
   ```powershell
   .\download_model.ps1
   ```

4. **Run the application**:
   ```powershell
   .\venv\Scripts\Activate.ps1
   python main.py
   ```

## Docker Installation

For Docker-based installation, refer to the main README.md file in the repository root.

## Manual Model Download

If the automatic model download fails, you can manually download the Phi-3-mini-4k-instruct-q4.gguf model from:
https://huggingface.co/microsoft/phi-3-mini-4k-instruct/resolve/main/phi-3-mini-4k-instruct-q4.gguf

Place the downloaded file in the `models/` directory and update the `config.yaml` file to point to the model path.

## Configuration

Edit the `config.yaml` file to customize the Guardian Node:

```yaml
llm:
  model_path: "models/phi-3-mini-4k-instruct-q4.gguf"  # Path to your GGUF model file
```

## Troubleshooting

- **Model not found**: Ensure the model file is in the correct location and the path in `config.yaml` is correct.
- **Python version error**: Make sure you have Python 3.8 or higher installed.
- **Dependency errors**: Try installing dependencies manually with `pip install -r requirements.txt`.
- **Permission denied**: Make sure the installation scripts have execute permissions (`chmod +x *.sh`).

## Next Steps

After installation, refer to the main README.md for usage instructions and features.