#!/bin/bash
# Authentication Compliance Check Script
# This script scans configuration files for password-based authentication
# and reports non-compliant configurations.

echo "Guardian Node Authentication Compliance Check"
echo "============================================="

# Check if running on Windows or Unix-based system
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    GREP_CMD="findstr"
    CONFIG_DIR="%USERPROFILE%\\.gitconfig"
    CREDENTIALS_FILE="%USERPROFILE%\\.git-credentials"
else
    GREP_CMD="grep"
    CONFIG_DIR="$HOME/.gitconfig"
    CREDENTIALS_FILE="$HOME/.git-credentials"
fi

# Function to check for password in Git config
check_git_config() {
    echo -e "\nChecking Git configuration..."
    
    # Check if credential.helper is set to store
    if git config --get credential.helper | $GREP_CMD "store" > /dev/null; then
        echo "[WARNING] Git credential store is enabled, which may store passwords in plaintext."
        echo "          Run: git config --global --unset credential.helper"
        ISSUES_FOUND=1
    fi
    
    # Check for credentials file
    if [[ -f "$CREDENTIALS_FILE" ]]; then
        echo "[WARNING] Git credentials file found at $CREDENTIALS_FILE"
        echo "          This file may contain plaintext passwords."
        echo "          Consider removing it and using PAT, SSH, or passkeys instead."
        ISSUES_FOUND=1
    fi
    
    # Check remote URLs for passwords
    echo -e "\nChecking remote URLs for passwords..."
    git remote -v | while read -r line; do
        if echo "$line" | $GREP_CMD -E "https://[^@]+:[^@]+@" > /dev/null; then
            echo "[ERROR] Detected password in Git remote URL: $line"
            echo "        Use PAT, SSH, or passkeys instead."
            ISSUES_FOUND=1
        fi
    done
    
    # Check authentication method
    echo -e "\nChecking authentication method..."
    if git remote -v | $GREP_CMD "git@github.com" > /dev/null; then
        echo "[OK] Using SSH authentication."
    elif git remote -v | $GREP_CMD -E "https://[^:]+@github.com" > /dev/null; then
        echo "[OK] Using PAT authentication."
    elif git remote -v | $GREP_CMD "https://github.com" > /dev/null; then
        echo "[WARNING] Using HTTPS without explicit authentication method."
        echo "          This may prompt for password, which is no longer supported by GitHub."
        echo "          Consider switching to PAT, SSH, or passkeys."
        ISSUES_FOUND=1
    fi
}

# Function to check for password in config files
check_config_files() {
    echo -e "\nScanning configuration files for password references..."
    
    # Check for password in config files
    find . -name "*.yaml" -o -name "*.yml" -o -name "*.json" -o -name "*.config" | while read -r file; do
        if $GREP_CMD -i "password" "$file" > /dev/null; then
            echo "[WARNING] Found password reference in $file"
            echo "          Please review this file to ensure no passwords are stored."
            ISSUES_FOUND=1
        fi
    done
}

# Main execution
ISSUES_FOUND=0

check_git_config
check_config_files

echo -e "\n============================================="
if [ $ISSUES_FOUND -eq 0 ]; then
    echo "✅ No authentication compliance issues found."
    echo "   All configurations appear to be using secure authentication methods."
else
    echo "❌ Authentication compliance issues found."
    echo "   Please review the warnings and errors above."
    echo "   See README.md for instructions on secure authentication methods."
fi

echo -e "\nRecommended Authentication Methods:"
echo "1. PAT (Personal Access Token)"
echo "2. SSH Keys"
echo "3. Passkeys (via GitHub CLI)"

exit $ISSUES_FOUND