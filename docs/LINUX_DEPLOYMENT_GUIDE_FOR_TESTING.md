## 🐧 Guardian Node: Linux Testing Deployment Guide

This guide details the steps required to validate the recently cleaned and refactored Guardian Node codebase within a Linux sandbox environment.

### Prerequisites

* A Linux machine (e.g., Ubuntu, Raspberry Pi OS).
* Docker and Docker Compose installed.
* The 'unzip' utility installed (`sudo apt install unzip`).
* The **'gemma model' binary file** (e.g., `gemma-2-2b-it-Q4_K_M.gguf`) saved separately.

### Step 1: Unarchive and Prepare

1. Transfer the `guardian_node_clean_for_linux.zip` file to your Linux machine.
2. Unzip the project archive:
   ```bash
   unzip guardian_node_clean_for_linux.zip
   ```
3. **Navigate** to the project directory:
   ```bash
   cd guardian_node_clean
   ```

### Step 2: Restore Model File (CRITICAL)

The model binary was removed from the source code for repository cleanliness. It must be restored for the LLM functionality to work.

1. **Create** the target model directory:
   ```bash
   mkdir -p guardian_interpreter/models
   ```
2. **Copy and Rename** your saved model file (`/path/to/your/gemma_model.gguf`) to the expected location and name:
   ```bash
   cp /path/to/your/gemma-2-2b-it-Q4_K_M.gguf guardian_interpreter/models/gemma-2-2b-it-Q4_K_M.gguf
   ```

### Step 3: Build and Run with Docker

1. **Build** the application image using the corrected Dockerfile:
   ```bash
   docker build -t guardian-node:latest .
   ```
2. **Start** the service in the background:
   ```bash
   docker-compose up -d
   ```
3. **Verify** the LLM model loaded successfully by checking the logs:
   ```bash
   docker logs -f guardian-node-container
   ```

### Step 4: Testing the Deployment

1. **Access the GUI** (if exposed):
   - Check `docker-compose.yml` for the exposed port
   - Navigate to `http://localhost:<port>` in your browser

2. **Run health checks**:
   ```bash
   docker exec guardian-node-container python guardian_interpreter/health_check.py
   ```

3. **Test LLM integration**:
   ```bash
   docker exec guardian-node-container python test_llm_integration.py
   ```

### Troubleshooting

**Model not found error:**
- Verify the model file exists: `ls -lh guardian_interpreter/models/`
- Check the model filename matches exactly what's configured in `config.yaml`

**Docker build fails:**
- Ensure all dependencies are in `requirements.txt`
- Check Docker logs: `docker logs guardian-node-container`

**Permission issues:**
- Run with sudo if needed: `sudo docker-compose up -d`

### Cleanup

To stop and remove the containers:
```bash
docker-compose down
```

To remove the image:
```bash
docker rmi guardian-node:latest
```
