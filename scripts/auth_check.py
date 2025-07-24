#!/usr/bin/env python3
"""
Authentication Configuration Verification Utility

This script verifies that the authentication configuration for the Guardian Node project
complies with security best practices, specifically ensuring that no password-based
authentication is being used. It checks Git configuration files and provides clear
error messages and remediation steps for any issues found.

Requirements:
- Python 3.8+
- Git installed and accessible in PATH

Usage:
    python auth_check.py [--fix] [--verbose]

Options:
    --fix       Attempt to fix detected issues automatically
    --verbose   Show detailed information about the checks being performed
"""

import os
import sys
import subprocess
import re
import argparse
import platform
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('auth_check')

# Authentication methods
AUTH_METHODS = {
    'PAT': {
        'name': 'Personal Access Token',
        'config_keys': ['credential.helper'],
        'valid_values': ['store', 'manager', 'cache', 'wincred', 'osxkeychain', 'libsecret'],
        'docs_url': 'https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token'
    },
    'SSH': {
        'name': 'SSH Key',
        'config_keys': ['core.sshCommand', 'url.*.insteadOf'],
        'docs_url': 'https://docs.github.com/en/authentication/connecting-to-github-with-ssh'
    },
    'PASSKEY': {
        'name': 'Passkey',
        'config_keys': ['credential.helper'],
        'valid_values': ['passkey'],
        'docs_url': 'https://docs.github.com/en/authentication/authenticating-with-a-passkey'
    }
}

# Insecure authentication patterns
INSECURE_PATTERNS = [
    {
        'pattern': r'https?://.*:.*@',
        'description': 'URL with embedded credentials',
        'file_patterns': ['.git/config', '.gitconfig', '**/.git-credentials'],
        'remediation': 'Remove credentials from URLs and use a credential helper instead'
    },
    {
        'pattern': r'credential\.username=',
        'description': 'Hardcoded username in Git config',
        'file_patterns': ['.git/config', '.gitconfig'],
        'remediation': 'Use a credential helper to manage authentication'
    },
    {
        'pattern': r'credential\.helper=store',
        'description': 'Unencrypted credential storage',
        'file_patterns': ['.git/config', '.gitconfig'],
        'remediation': 'Use an encrypted credential helper like "manager" or "osxkeychain"'
    }
]

def get_git_config(global_config=False):
    """Get Git configuration as a dictionary."""
    try:
        cmd = ['git', 'config', '--list']
        if global_config:
            cmd.append('--global')
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        config = {}
        
        for line in result.stdout.splitlines():
            if '=' in line:
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
        
        return config
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get Git configuration: {e}")
        return {}

def check_auth_method(config):
    """Check if a secure authentication method is configured."""
    detected_methods = []
    
    # Check for PAT configuration
    if any(key.startswith('credential.helper') for key in config.keys()):
        for key in [k for k in config.keys() if k.startswith('credential.helper')]:
            value = config[key]
            if any(v in value for v in AUTH_METHODS['PAT']['valid_values']):
                detected_methods.append('PAT')
                break
    
    # Check for SSH configuration
    if 'core.sshCommand' in config or any(key.startswith('url.') and key.endswith('.insteadOf') and 'ssh://' in config[key] for key in config.keys()):
        detected_methods.append('SSH')
    
    # Check for Passkey configuration
    if any(key.startswith('credential.helper') and 'passkey' in config[key] for key in config.keys()):
        detected_methods.append('PASSKEY')
    
    return detected_methods

def check_password_auth(config):
    """Check if password authentication is being used."""
    issues = []
    
    # Check for absence of secure auth methods
    detected_methods = check_auth_method(config)
    if not detected_methods:
        issues.append({
            'severity': 'HIGH',
            'message': 'No secure authentication method detected',
            'remediation': 'Configure either PAT, SSH key, or Passkey authentication'
        })
    
    # Check for insecure patterns in config
    for key, value in config.items():
        # Check for URLs with embedded credentials
        if re.search(r'https?://.*:.*@', value):
            issues.append({
                'severity': 'CRITICAL',
                'message': f'URL with embedded credentials found in {key}',
                'remediation': 'Remove credentials from URLs and use a credential helper instead'
            })
        
        # Check for explicit username configuration
        if key == 'credential.username':
            issues.append({
                'severity': 'MEDIUM',
                'message': 'Explicit username configuration found',
                'remediation': 'Use a credential helper to manage authentication'
            })
    
    # Check for unencrypted credential storage
    if any(key.startswith('credential.helper') and 'store' in config[key] for key in config.keys()):
        issues.append({
            'severity': 'MEDIUM',
            'message': 'Unencrypted credential storage detected',
            'remediation': 'Use an encrypted credential helper like "manager" or "osxkeychain"'
        })
    
    return issues

def check_git_credentials_file():
    """Check for the existence of .git-credentials file which may contain plaintext credentials."""
    issues = []
    
    # Check in home directory
    home_dir = Path.home()
    git_credentials = home_dir / '.git-credentials'
    
    if git_credentials.exists():
        issues.append({
            'severity': 'HIGH',
            'message': 'Found .git-credentials file which may contain plaintext credentials',
            'remediation': 'Delete this file and use a secure credential helper instead',
            'file_path': str(git_credentials)
        })
        
        # Check if it contains passwords
        try:
            with open(git_credentials, 'r') as f:
                content = f.read()
                if re.search(r'https?://.*:.*@', content):
                    issues.append({
                        'severity': 'CRITICAL',
                        'message': 'Plaintext credentials found in .git-credentials file',
                        'remediation': 'Delete this file immediately and change your passwords',
                        'file_path': str(git_credentials)
                    })
        except Exception as e:
            logger.warning(f"Could not read .git-credentials file: {e}")
    
    return issues

def fix_issues(issues, config):
    """Attempt to fix detected issues."""
    fixed = []
    failed = []
    
    for issue in issues:
        if issue['message'] == 'No secure authentication method detected':
            # Try to configure a credential helper based on the platform
            try:
                if platform.system() == 'Windows':
                    subprocess.run(['git', 'config', '--global', 'credential.helper', 'manager'], check=True)
                    fixed.append('Configured Git credential manager for Windows')
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.run(['git', 'config', '--global', 'credential.helper', 'osxkeychain'], check=True)
                    fixed.append('Configured osxkeychain credential helper for macOS')
                elif platform.system() == 'Linux':
                    # Try to detect available credential helpers
                    try:
                        subprocess.run(['git', 'credential-libsecret', 'get'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        subprocess.run(['git', 'config', '--global', 'credential.helper', 'libsecret'], check=True)
                        fixed.append('Configured libsecret credential helper for Linux')
                    except:
                        # Fall back to cache
                        subprocess.run(['git', 'config', '--global', 'credential.helper', 'cache --timeout=3600'], check=True)
                        fixed.append('Configured cache credential helper for Linux (limited security)')
            except Exception as e:
                failed.append(f"Failed to configure credential helper: {e}")
        
        elif 'URL with embedded credentials' in issue['message']:
            # This is complex to fix automatically, just provide guidance
            failed.append('URLs with embedded credentials must be manually removed')
        
        elif issue['message'] == 'Unencrypted credential storage detected':
            try:
                # Remove the insecure credential helper
                for key in [k for k in config.keys() if k.startswith('credential.helper') and 'store' in config[k]]:
                    subprocess.run(['git', 'config', '--global', '--unset', key], check=True)
                
                # Configure a secure one based on platform
                if platform.system() == 'Windows':
                    subprocess.run(['git', 'config', '--global', 'credential.helper', 'manager'], check=True)
                elif platform.system() == 'Darwin':
                    subprocess.run(['git', 'config', '--global', 'credential.helper', 'osxkeychain'], check=True)
                elif platform.system() == 'Linux':
                    try:
                        subprocess.run(['git', 'credential-libsecret', 'get'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        subprocess.run(['git', 'config', '--global', 'credential.helper', 'libsecret'], check=True)
                    except:
                        subprocess.run(['git', 'config', '--global', 'credential.helper', 'cache --timeout=3600'], check=True)
                
                fixed.append('Replaced unencrypted credential storage with secure alternative')
            except Exception as e:
                failed.append(f"Failed to replace credential helper: {e}")
        
        elif '.git-credentials file' in issue['message'] and 'file_path' in issue:
            # Warn but don't automatically delete credential files
            failed.append(f"Please manually delete {issue['file_path']} after ensuring credentials are saved securely")
    
    return fixed, failed

def print_auth_method_instructions(method):
    """Print instructions for setting up a specific authentication method."""
    if method == 'PAT':
        print("\nPersonal Access Token (PAT) Setup Instructions:")
        print("1. Visit GitHub > Settings > Developer settings > Personal access tokens")
        print("2. Generate a new token with appropriate scopes")
        print("3. Configure Git to use a credential helper:")
        print("   - Windows: git config --global credential.helper manager")
        print("   - macOS:   git config --global credential.helper osxkeychain")
        print("   - Linux:   git config --global credential.helper libsecret")
        print("4. The next time you perform a Git operation, enter your token as the password")
        print(f"For detailed instructions, visit: {AUTH_METHODS['PAT']['docs_url']}")
    
    elif method == 'SSH':
        print("\nSSH Key Setup Instructions:")
        print("1. Generate an SSH key pair:")
        print("   ssh-keygen -t ed25519 -C \"your_email@example.com\"")
        print("2. Add the key to the ssh-agent:")
        print("   - Windows: ssh-add ~/.ssh/id_ed25519")
        print("   - macOS/Linux: eval \"$(ssh-agent -s)\" && ssh-add ~/.ssh/id_ed25519")
        print("3. Add the public key to your GitHub account")
        print("4. Test the connection: ssh -T git@github.com")
        print("5. Update repository URLs to use SSH:")
        print("   git remote set-url origin git@github.com:username/repository.git")
        print(f"For detailed instructions, visit: {AUTH_METHODS['SSH']['docs_url']}")
    
    elif method == 'PASSKEY':
        print("\nPasskey Setup Instructions:")
        print("1. Visit GitHub > Settings > Password and authentication > Authentication methods")
        print("2. Register a new passkey following the prompts")
        print("3. Configure Git to use the passkey credential helper")
        print("4. The next time you perform a Git operation, you'll be prompted to use your passkey")
        print(f"For detailed instructions, visit: {AUTH_METHODS['PASSKEY']['docs_url']}")

def main():
    parser = argparse.ArgumentParser(description='Verify authentication configuration for Guardian Node')
    parser.add_argument('--fix', action='store_true', help='Attempt to fix detected issues')
    parser.add_argument('--verbose', action='store_true', help='Show detailed information')
    parser.add_argument('--ci', action='store_true', help='Run in non-interactive CI mode')
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    print("Guardian Node Authentication Configuration Check")
    print("===============================================")

    # Check Git installation
    try:
        git_version = subprocess.run(['git', '--version'], capture_output=True, text=True, check=True)
        logger.debug(f"Git version: {git_version.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("Git is not installed or not in PATH. Please install Git and try again.")
        sys.exit(1)

    # Get Git configuration
    logger.debug("Checking local Git configuration...")
    local_config = get_git_config()

    logger.debug("Checking global Git configuration...")
    global_config = get_git_config(global_config=True)

    # Combine configurations (local overrides global)
    config = {**global_config, **local_config}

    # Check for secure authentication methods
    detected_methods = check_auth_method(config)

    print("\nDetected Authentication Methods:")
    if detected_methods:
        for method in detected_methods:
            print(f"✓ {AUTH_METHODS[method]['name']}")
    else:
        print("✗ No secure authentication methods detected")

    # Check for password authentication
    logger.debug("Checking for password authentication...")
    issues = check_password_auth(config)

    # Check for .git-credentials file
    logger.debug("Checking for .git-credentials file...")
    git_credentials_issues = check_git_credentials_file()
    issues.extend(git_credentials_issues)

    # Display issues
    if issues:
        print("\nDetected Issues:")
        for issue in issues:
            severity_marker = "⚠️" if issue['severity'] in ['LOW', 'MEDIUM'] else "❌"
            print(f"{severity_marker} [{issue['severity']}] {issue['message']}")
            print(f"  Remediation: {issue['remediation']}")
            if 'file_path' in issue:
                print(f"  File: {issue['file_path']}")

        # Fix issues if requested
        if args.fix and not args.ci:
            print("\nAttempting to fix issues...")
            fixed, failed = fix_issues(issues, config)

            if fixed:
                print("\nFixed Issues:")
                for fix in fixed:
                    print(f"✓ {fix}")

            if failed:
                print("\nIssues requiring manual intervention:")
                for fail in failed:
                    print(f"✗ {fail}")
    else:
        print("\n✓ No authentication issues detected")

    # Provide setup instructions if no secure methods detected
    if not detected_methods and not args.ci:
        print("\nRecommended Authentication Methods:")
        print("1. SSH Key (most secure, works offline)")
        print("2. Personal Access Token (easy to set up)")
        print("3. Passkey (convenient, requires compatible hardware)")

        print("\nWould you like instructions for setting up a specific method? (1-3, or 'n' to skip)")
        choice = input("> ")

        if choice == '1':
            print_auth_method_instructions('SSH')
        elif choice == '2':
            print_auth_method_instructions('PAT')
        elif choice == '3':
            print_auth_method_instructions('PASSKEY')

    # Final recommendations
    if not args.ci:
        print("\nRecommendations:")
        print("- Ensure you're using a secure authentication method (PAT, SSH, or Passkey)")
        print("- Never store passwords in plain text or embed them in URLs")
        print("- Use encrypted credential helpers when available")
        print("- Regularly rotate your credentials for enhanced security")

    # Exit with appropriate status code
    if issues:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()