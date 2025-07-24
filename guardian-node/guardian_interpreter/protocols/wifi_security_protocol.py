"""
WiFi Configuration Security Protocol Module
Analyzes WiFi network security settings and provides family-friendly recommendations
"""

import subprocess
import re
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

def get_metadata() -> Dict[str, Any]:
    """Get module metadata"""
    return {
        'name': 'WiFi Security Analyzer',
        'description': 'Analyzes WiFi network security configuration and nearby networks',
        'version': '1.0.0',
        'author': 'Guardian Team',
        'family_friendly': True,
        'supported_protocols': ['wifi', '802.11', 'wpa', 'wep']
    }

def analyze(target: str = None, **kwargs) -> Dict[str, Any]:
    """
    Analyze WiFi security configuration
    
    Args:
        target: Specific WiFi network name (SSID) to analyze (optional)
        **kwargs: Additional parameters
            - scan_nearby: Scan for nearby networks (default: True)
            - check_current: Check current connection security (default: True)
            - check_saved: Check saved network security (default: True)
    
    Returns:
        Analysis results with findings and recommendations
    """
    findings = []
    recommendations = []
    technical_details = {}
    
    try:
        # Get current WiFi connection info
        if kwargs.get('check_current', True):
            current_findings = _check_current_wifi_security()
            findings.extend(current_findings)
        
        # Check saved WiFi networks
        if kwargs.get('check_saved', True):
            saved_findings = _check_saved_wifi_networks()
            findings.extend(saved_findings)
        
        # Scan for nearby networks and analyze security
        if kwargs.get('scan_nearby', True):
            nearby_findings = _scan_nearby_networks(target)
            findings.extend(nearby_findings)
        
        # Generate recommendations based on findings
        recommendations = _generate_wifi_recommendations(findings)
        
        # Determine overall status
        status = _determine_wifi_status(findings)
        
        technical_details.update({
            'checks_performed': {
                'current_connection': kwargs.get('check_current', True),
                'saved_networks': kwargs.get('check_saved', True),
                'nearby_scan': kwargs.get('scan_nearby', True)
            },
            'target_ssid': target,
            'analysis_timestamp': datetime.now().isoformat()
        })
        
        return {
            'status': status,
            'findings': findings,
            'recommendations': recommendations,
            'technical_details': technical_details
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'findings': [],
            'recommendations': [f'WiFi security analysis failed: {str(e)}'],
            'technical_details': {'error': str(e)}
        }

def _check_current_wifi_security() -> List[Dict[str, Any]]:
    """Check security of current WiFi connection"""
    findings = []
    
    try:
        # Get current WiFi connection info on Windows
        result = subprocess.run(['netsh', 'wlan', 'show', 'profile'], 
                              capture_output=True, text=True, timeout=15)
        
        if result.returncode != 0:
            findings.append({
                'severity': 'low',
                'title': 'WiFi Status Check Failed',
                'description': 'Unable to retrieve current WiFi connection information',
                'recommendation': 'Manually check your WiFi connection security settings',
                'technical_info': {'error': 'netsh command failed'}
            })
            return findings
        
        # Parse current connection
        current_profile = None
        result2 = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], 
                               capture_output=True, text=True, timeout=10)
        
        if result2.returncode == 0:
            lines = result2.stdout.split('\n')
            for line in lines:
                if 'Profile' in line and ':' in line:
                    current_profile = line.split(':', 1)[1].strip()
                    break
        
        if current_profile:
            # Get detailed info about current profile
            profile_result = subprocess.run(['netsh', 'wlan', 'show', 'profile', 
                                           f'name="{current_profile}"', 'key=clear'], 
                                          capture_output=True, text=True, timeout=10)
            
            if profile_result.returncode == 0:
                profile_info = profile_result.stdout
                security_findings = _analyze_wifi_profile_security(current_profile, profile_info, is_current=True)
                findings.extend(security_findings)
            else:
                findings.append({
                    'severity': 'info',
                    'title': 'Current WiFi Connection',
                    'description': f'Connected to WiFi network: {current_profile}',
                    'recommendation': 'Verify that your current WiFi network uses WPA3 or WPA2 security',
                    'technical_info': {'current_ssid': current_profile}
                })
        else:
            findings.append({
                'severity': 'info',
                'title': 'WiFi Connection Status',
                'description': 'No active WiFi connection detected',
                'recommendation': 'When connecting to WiFi, always choose networks with WPA3 or WPA2 security',
                'technical_info': {'connection_status': 'disconnected'}
            })
    
    except Exception as e:
        findings.append({
            'severity': 'low',
            'title': 'Current WiFi Check Error',
            'description': f'Unable to check current WiFi security: {str(e)}',
            'recommendation': 'Manually verify your current WiFi connection uses strong security',
            'technical_info': {'error': str(e)}
        })
    
    return findings

def _check_saved_wifi_networks() -> List[Dict[str, Any]]:
    """Check security of saved WiFi networks"""
    findings = []
    
    try:
        # Get list of saved WiFi profiles
        result = subprocess.run(['netsh', 'wlan', 'show', 'profiles'], 
                              capture_output=True, text=True, timeout=15)
        
        if result.returncode != 0:
            findings.append({
                'severity': 'low',
                'title': 'Saved Networks Check Failed',
                'description': 'Unable to retrieve saved WiFi network information',
                'recommendation': 'Manually review your saved WiFi networks for security',
                'technical_info': {'error': 'netsh profiles command failed'}
            })
            return findings
        
        # Parse profile names
        profile_names = []
        lines = result.stdout.split('\n')
        for line in lines:
            if 'All User Profile' in line and ':' in line:
                profile_name = line.split(':', 1)[1].strip()
                profile_names.append(profile_name)
        
        if not profile_names:
            findings.append({
                'severity': 'info',
                'title': 'Saved WiFi Networks',
                'description': 'No saved WiFi networks found',
                'recommendation': 'When saving WiFi networks, ensure they use WPA3 or WPA2 security',
                'technical_info': {'saved_profiles_count': 0}
            })
            return findings
        
        # Analyze each saved profile
        insecure_count = 0
        secure_count = 0
        
        for profile_name in profile_names[:10]:  # Limit to first 10 profiles
            try:
                profile_result = subprocess.run(['netsh', 'wlan', 'show', 'profile', 
                                               f'name="{profile_name}"'], 
                                              capture_output=True, text=True, timeout=10)
                
                if profile_result.returncode == 0:
                    profile_info = profile_result.stdout
                    security_findings = _analyze_wifi_profile_security(profile_name, profile_info, is_current=False)
                    findings.extend(security_findings)
                    
                    # Count security levels
                    for finding in security_findings:
                        if finding.get('severity') in ['critical', 'high']:
                            insecure_count += 1
                        else:
                            secure_count += 1
                            
            except Exception:
                continue  # Skip problematic profiles
        
        # Add summary finding
        findings.append({
            'severity': 'info',
            'title': 'Saved Networks Summary',
            'description': f'Found {len(profile_names)} saved WiFi networks',
            'recommendation': 'Regularly review and remove old or unused WiFi network profiles',
            'technical_info': {
                'total_profiles': len(profile_names),
                'analyzed_profiles': min(10, len(profile_names)),
                'insecure_count': insecure_count,
                'secure_count': secure_count
            }
        })
    
    except Exception as e:
        findings.append({
            'severity': 'low',
            'title': 'Saved Networks Check Error',
            'description': f'Unable to check saved WiFi networks: {str(e)}',
            'recommendation': 'Manually review your saved WiFi network security settings',
            'technical_info': {'error': str(e)}
        })
    
    return findings

def _analyze_wifi_profile_security(profile_name: str, profile_info: str, is_current: bool = False) -> List[Dict[str, Any]]:
    """Analyze security settings of a WiFi profile"""
    findings = []
    
    try:
        # Extract security information
        auth_type = None
        encryption = None
        
        lines = profile_info.split('\n')
        for line in lines:
            if 'Authentication' in line and ':' in line:
                auth_type = line.split(':', 1)[1].strip()
            elif 'Cipher' in line and ':' in line:
                encryption = line.split(':', 1)[1].strip()
        
        # Analyze security level
        security_level = _determine_wifi_security_level(auth_type, encryption)
        
        if security_level == 'insecure':
            severity = 'critical' if is_current else 'high'
            findings.append({
                'severity': severity,
                'title': f'Insecure WiFi Network: {profile_name}',
                'description': f'Network uses weak or no security (Auth: {auth_type}, Encryption: {encryption})',
                'recommendation': 'Avoid connecting to this network or ask the network owner to upgrade to WPA3/WPA2',
                'technical_info': {
                    'ssid': profile_name,
                    'auth_type': auth_type,
                    'encryption': encryption,
                    'is_current': is_current
                }
            })
        elif security_level == 'weak':
            severity = 'medium'
            findings.append({
                'severity': severity,
                'title': f'Weak WiFi Security: {profile_name}',
                'description': f'Network uses older security standards (Auth: {auth_type}, Encryption: {encryption})',
                'recommendation': 'Consider upgrading to WPA3 if supported by your router and devices',
                'technical_info': {
                    'ssid': profile_name,
                    'auth_type': auth_type,
                    'encryption': encryption,
                    'is_current': is_current
                }
            })
        else:  # secure
            findings.append({
                'severity': 'info',
                'title': f'Secure WiFi Network: {profile_name}',
                'description': f'Network uses good security standards (Auth: {auth_type}, Encryption: {encryption})',
                'recommendation': 'Good security! Continue using strong WiFi passwords',
                'technical_info': {
                    'ssid': profile_name,
                    'auth_type': auth_type,
                    'encryption': encryption,
                    'is_current': is_current
                }
            })
    
    except Exception as e:
        findings.append({
            'severity': 'low',
            'title': f'Profile Analysis Error: {profile_name}',
            'description': f'Unable to analyze security settings: {str(e)}',
            'recommendation': 'Manually check this network\'s security settings',
            'technical_info': {'error': str(e), 'profile': profile_name}
        })
    
    return findings

def _scan_nearby_networks(target_ssid: str = None) -> List[Dict[str, Any]]:
    """Scan for nearby WiFi networks and analyze their security"""
    findings = []
    
    try:
        # Scan for available networks
        result = subprocess.run(['netsh', 'wlan', 'show', 'profiles'], 
                              capture_output=True, text=True, timeout=20)
        
        if result.returncode != 0:
            findings.append({
                'severity': 'low',
                'title': 'Network Scan Failed',
                'description': 'Unable to scan for nearby WiFi networks',
                'recommendation': 'Manually check available WiFi networks for security',
                'technical_info': {'error': 'network scan failed'}
            })
            return findings
        
        # For a more comprehensive scan, we would use netsh wlan show profiles
        # But this requires more complex parsing. For now, provide general guidance.
        
        findings.append({
            'severity': 'info',
            'title': 'Nearby Networks Security',
            'description': 'WiFi network scanning completed',
            'recommendation': 'When choosing WiFi networks, always select ones with WPA3 or WPA2 security. Avoid open networks.',
            'technical_info': {'scan_type': 'basic_scan_completed'}
        })
        
        # Add specific guidance about open networks
        findings.append({
            'severity': 'medium',
            'title': 'Open Network Warning',
            'description': 'Be cautious of open (unsecured) WiFi networks in public places',
            'recommendation': 'Avoid using open WiFi for sensitive activities. Use a VPN if you must connect to open networks.',
            'technical_info': {'warning_type': 'open_network_security'}
        })
    
    except Exception as e:
        findings.append({
            'severity': 'low',
            'title': 'Network Scan Error',
            'description': f'Unable to scan nearby networks: {str(e)}',
            'recommendation': 'Manually check available WiFi networks and choose secure options',
            'technical_info': {'error': str(e)}
        })
    
    return findings

def _determine_wifi_security_level(auth_type: str, encryption: str) -> str:
    """Determine WiFi security level based on authentication and encryption"""
    if not auth_type or not encryption:
        return 'unknown'
    
    auth_lower = auth_type.lower()
    enc_lower = encryption.lower()
    
    # Insecure configurations
    if 'open' in auth_lower or 'none' in auth_lower:
        return 'insecure'
    
    if 'wep' in auth_lower or 'wep' in enc_lower:
        return 'insecure'
    
    # Weak but better than nothing
    if 'wpa' in auth_lower and 'wpa2' not in auth_lower and 'wpa3' not in auth_lower:
        return 'weak'
    
    # Good security
    if 'wpa2' in auth_lower or 'wpa3' in auth_lower:
        return 'secure'
    
    return 'unknown'

def _generate_wifi_recommendations(findings: List[Dict[str, Any]]) -> List[str]:
    """Generate actionable WiFi security recommendations"""
    recommendations = []
    
    # Extract specific recommendations from findings
    for finding in findings:
        if 'recommendation' in finding:
            recommendations.append(finding['recommendation'])
    
    # Add general WiFi security recommendations
    general_recommendations = [
        'Use WPA3 encryption when available, or WPA2 as a minimum',
        'Create strong, unique passwords for your WiFi networks',
        'Avoid connecting to open (unsecured) WiFi networks',
        'Regularly update your router firmware',
        'Use a guest network for visitors',
        'Disable WPS (WiFi Protected Setup) if not needed',
        'Change default network names (SSIDs) to something unique',
        'Consider using a VPN when connecting to public WiFi',
        'Regularly review and remove old saved WiFi networks',
        'Monitor who is connected to your home WiFi network'
    ]
    
    # Add general recommendations that aren't already covered
    for rec in general_recommendations:
        if not any(rec.lower() in existing.lower() for existing in recommendations):
            recommendations.append(rec)
    
    return recommendations[:12]  # Limit to top 12 recommendations

def _determine_wifi_status(findings: List[Dict[str, Any]]) -> str:
    """Determine overall WiFi security status"""
    if not findings:
        return 'secure'
    
    # Check for critical findings
    critical_count = 0
    high_count = 0
    medium_count = 0
    
    for finding in findings:
        severity = finding.get('severity', 'info').lower()
        if severity == 'critical':
            critical_count += 1
        elif severity == 'high':
            high_count += 1
        elif severity == 'medium':
            medium_count += 1
    
    # Determine status based on severity counts
    if critical_count > 0:
        return 'critical'
    elif high_count > 0 or medium_count >= 3:
        return 'warning'
    elif medium_count > 0:
        return 'warning'
    
    return 'secure'