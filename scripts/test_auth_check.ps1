# Test script for auth_check.py
Write-Host "Testing auth_check.py..."
python scripts/auth_check.py --verbose
if ($LASTEXITCODE -eq 0) {
    Write-Host "Test passed: No authentication issues detected"
} else {
    Write-Host "Test failed: Authentication issues detected"
}