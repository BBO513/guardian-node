# Authentication Check Utility

This utility verifies that the authentication configuration for the Guardian Node project complies with security best practices, specifically ensuring that no password-based authentication is being used.

## Features

- Detects secure authentication methods (PAT, SSH keys, Passkeys)
- Identifies password-based authentication
- Checks for insecure credential storage
- Provides clear error messages and remediation steps
- Can automatically fix some common issues

## Requirements

- Python 3.8+
- Git installed and accessible in PATH

## Usage

```bash
# Basic usage
python auth_check.py

# Show detailed information
python auth_check.py --verbose

# Attempt to fix detected issues
python auth_check.py --fix
```

## Authentication Methods

The utility checks for the following secure authentication methods:

1. **Personal Access Tokens (PAT)**: Detected by checking for credential helpers in Git configuration
2. **SSH Keys**: Detected by checking for SSH command configuration or SSH URLs
3. **Passkeys**: Detected by checking for passkey credential helper

## Issues Detected

The utility checks for the following issues:

- No secure authentication method configured
- URLs with embedded credentials
- Explicit username configuration in Git config
- Unencrypted credential storage
- Presence of .git-credentials file with plaintext credentials

## Automatic Fixes

When run with the `--fix` flag, the utility can automatically fix some issues:

- Configure appropriate credential helper based on platform
- Replace unencrypted credential storage with secure alternatives

## Exit Codes

- 0: No authentication issues detected
- 1: Authentication issues detected

## Integration

This utility can be integrated into CI/CD pipelines to enforce secure authentication practices.

Example GitHub Actions workflow:

```yaml
name: Authentication Check

on: [push, pull_request]

jobs:
  auth-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - name: Run authentication check
        run: python scripts/auth_check.py
```