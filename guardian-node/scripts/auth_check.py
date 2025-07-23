#!/usr/bin/env python3
"""
Authentication Configuration Verification Utility

This script verifies that Git authentication is configured securely,
without using password-based authentication.

Usage:
    python auth_check.py [--fix]

Options:
    --fix    Attempt to fix insecure authentication configurations
"""

import os
import sys
import subprocess
import re
import argparse


def check_git_config():
    """Check Git configuration for password-based authentication."""
    try:
        # Check if credential helper is configured
        result = subprocess.run(
            ["git", "config", "--get", "credential.helper"],
            capture_output=True,
            text=True
        )
        
        if "store" in result.stdout:
            print("[WARNING] Git credential store is enabled, which may store passwords in plaintext.")
            return False
            
        # Check remote URL format
        result = subprocess.run(
            ["git", "remote", "-v"],
            capture_output=True,
            text=True
        )
        
        # Look for URLs that might contain passwords
        if re.search(r"https://[^@]+:[^@]+@", result.stdout):
            print("[ERROR] Detected password in Git remote URL. Use PAT, SSH, or passkeys instead.")
            return False
            
        # Check for SSH or PAT usage
        if re.search(r"git@github\.com", result.stdout):
            print("[OK] Using SSH authentication.")
            return True
        elif re.search(r"https://[^:]+@github\.com", result.stdout):
            print("[OK] Using PAT authentication.")
            return True
        elif re.search(r"https://github\.com", result.stdout):
            print("[WARNING] Using HTTPS without explicit authentication method.")
            print("          This may prompt for password, which is no longer supported by GitHub.")
            print("          Consider switching to PAT, SSH, or passkeys.")
            return False
            
        return True
    except Exception as e:
        print(f"[ERROR] Failed to check Git configuration: {e}")
        return False


def fix_git_config():
    """Attempt to fix insecure Git authentication configurations."""
    try:
        # Disable credential store if it's enabled
        result = subprocess.run(
            ["git", "config", "--get", "credential.helper"],
            capture_output=True,
            text=True
        )
        
        if "store" in result.stdout:
            subprocess.run(["git", "config", "--unset", "credential.helper"])
            print("[FIXED] Disabled Git credential store.")
            
        # Check if we need to suggest authentication methods
        result = subprocess.run(
            ["git", "remote", "-v"],
            capture_output=True,
            text=True
        )
        
        if re.search(r"https://github\.com", result.stdout) and not re.search(r"https://[^:]+@github\.com", result.stdout):
            print("\n[ACTION REQUIRED] Please set up secure authentication:")
            print("\n1. For PAT (Personal Access Token):")
            print("   a. Generate a token at https://github.com/settings/tokens")
            print("   b. Run: git remote set-url origin https://YOUR_PAT@github.com/USER/REPO.git")
            print("\n2. For SSH:")
            print("   a. Generate SSH key: ssh-keygen -t ed25519")
            print("   b. Add key to GitHub: https://github.com/settings/keys")
            print("   c. Run: git remote set-url origin git@github.com:USER/REPO.git")
            print("\n3. For Passkeys:")
            print("   a. Install GitHub CLI: https://cli.github.com/")
            print("   b. Run: gh auth login")
            
        return True
    except Exception as e:
        print(f"[ERROR] Failed to fix Git configuration: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Verify Git authentication configuration")
    parser.add_argument("--fix", action="store_true", help="Attempt to fix insecure configurations")
    args = parser.parse_args()
    
    print("Guardian Node Authentication Check")
    print("=================================")
    
    secure = check_git_config()
    
    if not secure and args.fix:
        print("\nAttempting to fix insecure configurations...")
        fix_git_config()
    elif not secure:
        print("\nRun with --fix to attempt automatic fixes.")
        
    print("\nRecommended Authentication Methods:")
    print("1. PAT (Personal Access Token)")
    print("2. SSH Keys")
    print("3. Passkeys (via GitHub CLI)")
    print("\nFor detailed instructions, see the Authentication section in README.md")
    
    if not secure:
        sys.exit(1)


if __name__ == "__main__":
    main()