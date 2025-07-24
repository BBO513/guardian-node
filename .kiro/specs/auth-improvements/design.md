# Design Document: Authentication Improvements

## Overview

This design document outlines the approach for implementing secure authentication methods across the Guardian Node project. The implementation will focus on eliminating password-based authentication and standardizing on Personal Access Tokens (PATs), SSH keys, and passkeys as the only acceptable authentication methods. This aligns with GitHub's security practices and enhances the overall security posture of the Guardian Node system.

## Architecture

The authentication improvements will be implemented across three main areas:

1. **Documentation Updates**: Comprehensive updates to README.md and other documentation files to clearly explain secure authentication methods.
2. **Configuration Scripts**: Updates to setup scripts to enforce and facilitate secure authentication.
3. **Verification Mechanisms**: Implementation of tests to verify that authentication methods are working correctly and securely.

The architecture will maintain the Guardian Node's core principle of offline-first operation, ensuring all authentication methods work without requiring internet connectivity for local operations.

## Components and Interfaces

### Documentation Component

This component will provide clear, comprehensive instructions for setting up each authentication method:

- **README.md**: Primary documentation file with authentication section
- **CONTRIBUTING.md**: Guidelines for contributors including authentication requirements
- **AUTH_GUIDE.md**: Detailed guide for each authentication method with platform-specific instructions

### Configuration Scripts Component

Scripts will be updated to support secure authentication methods:

- **setup.sh/setup.ps1**: Initial setup scripts that configure authentication
- **auth_check.py**: Python utility to verify authentication method compliance
- **git_config_helper.py**: Helper script to configure Git for secure authentication

### Verification Component

Tests and verification mechanisms:

- **test_auth_config.py**: Tests to verify authentication configuration
- **auth_compliance_check.sh**: Shell script to check for password-based authentication in configuration files

## Data Models

### Authentication Method Model

```python
class AuthMethod:
    def __init__(self, method_type, config_path, platform_support):
        self.method_type = method_type  # PAT, SSH, or Passkey
        self.config_path = config_path  # Path to configuration file
        self.platform_support = platform_support  # List of supported platforms
        self.setup_instructions = []  # List of setup steps
        
    def validate(self):
        # Validate the authentication method configuration
        pass
        
    def generate_instructions(self):
        # Generate platform-specific instructions
        pass
```

### Authentication Configuration Model

```python
class AuthConfig:
    def __init__(self):
        self.methods = []  # List of configured AuthMethod objects
        self.default_method = None  # Default authentication method
        self.last_verified = None  # Timestamp of last verification
        
    def add_method(self, method):
        # Add an authentication method
        pass
        
    def verify_compliance(self):
        # Verify compliance with no-password policy
        pass
        
    def save_config(self):
        # Save configuration to file
        pass
```

## Error Handling

The authentication system will implement the following error handling strategies:

1. **Clear Error Messages**: All authentication errors will provide clear, actionable messages.
2. **Guided Recovery**: When authentication fails, the system will guide users through recovery steps.
3. **Fallback Mechanisms**: If primary authentication fails, the system will suggest alternative methods.
4. **Logging**: Authentication failures will be logged for troubleshooting.

Error scenarios and responses:

| Error Scenario | Response |
|----------------|----------|
| Invalid PAT | Provide instructions to generate a new PAT with correct scopes |
| SSH key issues | Guide through SSH key verification and troubleshooting |
| Passkey not recognized | Steps to register or recover passkey |
| Attempted password use | Explain password authentication is disabled and suggest alternatives |

## Testing Strategy

The testing strategy will focus on verifying that:

1. All documentation accurately reflects the supported authentication methods
2. Setup scripts correctly configure secure authentication
3. No password-based authentication is possible
4. All authentication methods work in offline mode

Test cases will include:

- Verification that README.md contains accurate authentication instructions
- Validation that setup scripts configure Git for secure authentication
- Confirmation that authentication works across different platforms
- Checks that error messages are clear and helpful
- Verification that offline authentication works correctly

### Test Implementation

```python
def test_no_password_auth():
    """Test that password authentication is not possible."""
    # Attempt password authentication and verify it fails
    result = subprocess.run(["git", "push", "--dry-run"], 
                           input="username\npassword", 
                           capture_output=True, 
                           text=True)
    assert "Authentication failed" in result.stderr
    
def test_pat_auth():
    """Test that PAT authentication works."""
    # Configure Git with a test PAT
    setup_pat_auth("test_pat")
    # Attempt a Git operation
    result = subprocess.run(["git", "fetch", "--dry-run"], 
                           capture_output=True, 
                           text=True)
    assert result.returncode == 0
    
def test_ssh_auth():
    """Test that SSH authentication works."""
    # Configure Git with SSH
    setup_ssh_auth("test_key")
    # Attempt a Git operation
    result = subprocess.run(["git", "fetch", "--dry-run"], 
                           capture_output=True, 
                           text=True)
    assert result.returncode == 0
```

## Implementation Considerations

1. **Backward Compatibility**: The implementation will need to handle existing configurations gracefully, migrating users to secure authentication methods.
2. **Platform Differences**: Instructions and scripts must account for differences between Windows, Linux, and macOS.
3. **Offline Operation**: All authentication methods must work in offline mode for local operations.
4. **User Experience**: The authentication process should be straightforward with clear guidance.
5. **Security**: The implementation must not introduce new security vulnerabilities.

## Documentation Plan

The documentation will be updated to include:

1. Clear instructions for each authentication method in README.md
2. Detailed troubleshooting guide for authentication issues
3. Platform-specific instructions for Windows, Linux, and macOS
4. Visual guides (diagrams or screenshots) for complex setup steps
5. FAQ section addressing common authentication questions