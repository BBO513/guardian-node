# Changelog

This document outlines the recent changes made to the project to fix the Docker build process and improve the overall stability of the application.

## Summary

The primary goal was to resolve a series of issues that were preventing the Docker container from building and running successfully. This involved fixing problems with the `Dockerfile`, managing dependencies, and correcting file paths.

## Changes

### 1. Resolved Dockerfile Merge Conflict

The initial problem was a merge conflict in the `Dockerfile` that was preventing the Docker build from starting. This was resolved by removing the conflict markers from the file.

### 2. Created `.dockerignore`

The Docker build was failing because it was trying to copy the `venv` directory into the image. A `.dockerignore` file was created to exclude the `venv` directory, as well as other unnecessary files like `.git`, `.vscode`, and `__pycache__`, from the build context. This resolved the build error and reduced the size of the build context.

### 3. Fixed `requirements.txt`

The `requirements.txt` file contained an erroneous "EOF" marker at the end of the file, which was causing the `pip install` command to fail during the Docker build. This was removed to ensure that all dependencies could be installed correctly.

### 4. Added `PyYAML` Dependency

The application was failing to start because the `PyYAML` package was not listed in the `requirements.txt` file. This dependency was added to ensure that the application could correctly parse the `config.yaml` file at runtime.

### 5. Corrected File Paths

The application was unable to find several key files due to incorrect paths:

*   **`config.yaml`**: The path to the `config.yaml` file was corrected in `guardian_interpreter/main.py` to point to the correct location within the Docker container.
*   **`skills` directory**: The path to the `skills` directory was corrected in `guardian_interpreter/main.py`.
*   **LLM Model**: The path to the LLM model in `guardian_interpreter/config.yaml` was updated to be a relative path, allowing the application to find the model within the container.

### 6. Kept Container Alive

The Docker container was exiting immediately after starting because the main application is an interactive CLI. To resolve this, the `Dockerfile` was modified to use `tail -f /dev/null` as the main command. This keeps the container running in the background, allowing you to attach to it and run the application interactively.

### 7. Installed `portaudio` Dependency

The Docker build was failing because the `pyaudio` package could not be installed. This was resolved by installing the `portaudio19-dev` package in the `Dockerfile`.

## How to Run the Application

To run the application, you can now use the following commands:

1.  **Build the Docker image:**
    ```bash
    docker build . -f Dockerfile -t guardian-interpreter
    ```

2.  **Run the container in the background:**
    ```bash
    docker run -d -p 8080:8080 guardian-interpreter
    ```

3.  **Get the container ID:**
    ```bash
    docker ps
    ```

4.  **Access the container's shell:**
    ```bash
    docker exec -it <container_id> /bin/bash
    ```

5.  **Run the application:**
    ```bash
    python3 guardian_interpreter/main.py
    ```

## Committing and Pushing Changes

To commit and push the changes to the `production-full-pr` branch, use the following commands:

1.  **Stage the changes:**
    ```bash
    git add .
    ```

2.  **Commit the changes:**
    ```bash
    git commit -m "fix: Resolve Docker build issues"
    ```

3.  **Push the changes:**
    ```bash
    git push origin production-full-pr
    ```
