"""
Parental Control Protocol Module
Comprehensive parental control system analysis including content filtering, 
device monitoring, time restrictions, and social media privacy
"""

import subprocess
import platform
import re
from typing import Dict, List, Any, Optional
from datetime import datetime

def get_metadata() -> Dict[str, Any]:
    """Get module metadata."""
    return {
        'name': 'Parental Control Protocol',
        'description': 'Comprehensive parental control system analysis including content filtering, device monitoring, time restrictions, and social media privacy',
        'version': '1.0.0',
        'author': 'Guardian Team',
        'family_friendly': True,
        'supported_protocols': ['content_filtering', 'device_monitoring', 'time_restrictions', 'social_media_privacy']
    }

def analyze(target: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """
    Analyze parental control systems and configurations.
    Returns dict with status, findings, recommendations, and technical_details.
    """
    findings = []
    recommendations = []
    technical_details = {}
    
    try:
        family_profile = kwargs.get('family_profile', {})
        
        # Content filtering
        if kwargs.get('check_content_filtering', True):
            findings.extend(_analyze_content_filtering(family_profile))
        
        # Device monitoring
        if kwargs.get('check_device_monitoring', True):
            findings.extend(_analyze_device_monitoring(family_profile))
        
        # Time restrictions
        if kwargs.get('check_time_restrictions', True):
            findings.extend(_analyze_time_restrictions(family_profile))
        
        # Social media privacy
        if kwargs.get('check_social_media_privacy', True):
            findings.extend(_analyze_social_media_privacy(family_profile))
        
        recommendations = _generate_parental_control_recommendations(findings, family_profile)
        status = _determine_overall_status(findings)
        
        technical_details.update({
            'checks_performed': {
                'content_filtering': kwargs.get('check_content_filtering', True),
                'device_monitoring': kwargs.get('check_device_monitoring', True),
                'time_restrictions': kwargs.get('check_time_restrictions', True),
                'social_media_privacy': kwargs.get('check_social_media_privacy', True)
            },
            'family_profile_provided': bool(family_profile),
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
            'recommendations': [f'Parental control analysis failed: {str(e)}'],
            'technical_details': {'error': str(e)}
        }

def _analyze_content_filtering(family_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Analyze content filtering systems and settings."""
    findings = []
    
    try:
        findings.extend(_check_dns_filtering(family_profile))
        findings.extend(_check_parental_control_software(family_profile))
        findings.extend(_check_builtin_parental_controls(family_profile))
    except Exception as e:
        findings.append(_create_finding(
            'low', 'Content Filtering Analysis Error',
            f'Unable to complete content filtering analysis: {str(e)}',
            'Manually review your content filtering settings',
            {'error': str(e)}
        ))
    
    return findings

def _analyze_device_monitoring(family_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Analyze device monitoring capabilities and settings."""
    findings = []
    
    try:
        findings.extend(_detect_monitoring_software(family_profile))
        findings.extend(_check_screen_time_controls(family_profile))
    except Exception as e:
        findings.append(_create_finding(
            'low', 'Device Monitoring Analysis Error',
            f'Unable to complete device monitoring analysis: {str(e)}',
            'Manually review your device monitoring settings',
            {'error': str(e)}
        ))
    
    return findings

def _analyze_time_restrictions(family_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Analyze time restriction settings and controls."""
    findings = []
    
    try:
        findings.extend(_check_screen_time_controls(family_profile))
        
        if platform.system() == "Windows":
            findings.append(_create_finding(
                'info', 'Time Restrictions Check',
                'Windows Family Safety time restrictions require manual verification',
                'Check Windows Family Safety settings for time restrictions and bedtime controls',
                {'platform': 'Windows', 'check_type': 'manual_verification'}
            ))
    except Exception as e:
        findings.append(_create_finding(
            'low', 'Time Restrictions Analysis Error',
            f'Unable to complete time restrictions analysis: {str(e)}',
            'Manually review your time restriction settings',
            {'error': str(e)}
        ))
    
    return findings

def _analyze_social_media_privacy(family_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Analyze social media privacy settings and recommendations."""
    findings = []
    
    try:
        family_members = family_profile.get('members', [])
        if family_members:
            findings.extend(_get_age_appropriate_social_media_guidance(family_members))
        else:
            findings.append(_create_finding(
                'info', 'Social Media Privacy Guidance',
                'General social media privacy recommendations available',
                'Configure privacy settings on all social media platforms used by family members',
                {'guidance_type': 'general'}
            ))
        
        findings.extend(_get_platform_privacy_recommendations())
    except Exception as e:
        findings.append(_create_finding(
            'low', 'Social Media Privacy Analysis Error',
            f'Unable to complete social media privacy analysis: {str(e)}',
            'Manually review social media privacy settings for all family members',
            {'error': str(e)}
        ))
    
    return findings

def _check_dns_filtering(family_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Check for DNS-based content filtering."""
    findings = []
    
    try:
        system = platform.system()
        family_dns_servers = [
            '208.67.222.123', '208.67.220.123',  # OpenDNS FamilyShield
            '185.228.168.168', '185.228.169.168',  # CleanBrowsing Family
            '1.1.1.3', '1.0.0.3'  # Cloudflare for Families
        ]
        dns_servers = []
        
        if system == "Windows":
            result = subprocess.run(['ipconfig', '/all'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'DNS Servers' in line:
                        dns_servers += re.findall(r'\d+\.\d+\.\d+\.\d+', line)
        elif system in ["Linux", "Darwin"]:
            try:
                with open('/etc/resolv.conf', 'r') as f:
                    resolv_content = f.read()
                    dns_servers += re.findall(r'nameserver\s+(\d+\.\d+\.\d+\.\d+)', resolv_content)
            except FileNotFoundError:
                findings.append(_create_finding(
                    'low', 'DNS Configuration Check Failed',
                    'Unable to read DNS configuration',
                    'Manually check DNS settings for family-safe filtering',
                    {'error': 'resolv.conf not found'}
                ))
        
        using_family_dns = any(dns in family_dns_servers for dns in dns_servers)
        
        if using_family_dns:
            findings.append(_create_finding(
                'info', 'Family-Safe DNS Detected',
                'System is using family-safe DNS filtering service',
                'Continue using family-safe DNS and regularly review filtering settings',
                {'dns_servers': dns_servers, 'family_safe': True}
            ))
        else:
            findings.append(_create_finding(
                'medium', 'No DNS Content Filtering',
                'System is not using family-safe DNS filtering',
                'Consider switching to a family-safe DNS service',
                {'dns_servers': dns_servers, 'family_safe': False}
            ))
    except Exception as e:
        findings.append(_create_finding(
            'low', 'DNS Filtering Check Error',
            f'Unable to check DNS filtering: {str(e)}',
            'Manually verify DNS filtering settings',
            {'error': str(e)}
        ))
    
    return findings

def _check_parental_control_software(family_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Check for installed parental control software."""
    findings = []
    
    try:
        system = platform.system()
        detected_software = []
        
        if system == "Windows":
            result = subprocess.run(['tasklist'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                processes = result.stdout.lower()
                parental_software = {
                    'qustodio': 'Qustodio',
                    'norton': 'Norton Family',
                    'bark': 'Bark',
                    'circle': 'Circle Home Plus',
                    'kaspersky': 'Kaspersky Safe Kids',
                    'bitdefender': 'Bitdefender Parental Control'
                }
                
                for pname, sname in parental_software.items():
                    if pname in processes:
                        detected_software.append(sname)
        elif system in ["Linux", "Darwin"]:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                processes = result.stdout.lower()
                for pname in ['qustodio-daemon', 'circle', 'bark-agent']:
                    if pname in processes:
                        detected_software.append(pname)
        
        if detected_software:
            findings.append(_create_finding(
                'info', 'Parental Control Software Detected',
                f'Found parental control software: {", ".join(detected_software)}',
                'Ensure parental control software is properly configured and up to date',
                {'detected_software': detected_software}
            ))
        else:
            findings.append(_create_finding(
                'medium', 'No Parental Control Software',
                'No parental control software detected',
                'Consider installing parental control software for comprehensive family protection',
                {'detected_software': []}
            ))
    except Exception as e:
        findings.append(_create_finding(
            'low', 'Parental Control Software Check Error',
            f'Unable to check for parental control software: {str(e)}',
            'Manually verify parental control software installation',
            {'error': str(e)}
        ))
    
    return findings

def _check_builtin_parental_controls(family_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Check for built-in parental control features."""
    findings = []
    
    try:
        system = platform.system()
        
        if system == "Windows":
            findings.append(_create_finding(
                'info', 'Windows Family Safety',
                'Windows includes built-in Family Safety features',
                'Configure Windows Family Safety through Microsoft Family accounts for comprehensive parental controls',
                {'platform': 'Windows', 'feature': 'Family Safety'}
            ))
        elif system == "Darwin":
            findings.append(_create_finding(
                'info', 'macOS Parental Controls',
                'macOS includes built-in Screen Time and Parental Controls',
                'Configure Screen Time and Parental Controls in System Preferences for family protection',
                {'platform': 'macOS', 'feature': 'Screen Time & Parental Controls'}
            ))
        else:
            findings.append(_create_finding(
                'info', 'Built-in Parental Controls',
                'Check your operating system for built-in parental control features',
                'Many modern operating systems include parental control features',
                {'platform': system}
            ))
    except Exception as e:
        findings.append(_create_finding(
            'low', 'Built-in Controls Check Error',
            f'Unable to check built-in parental controls: {str(e)}',
            'Manually check your operating system\'s parental control features',
            {'error': str(e)}
        ))
    
    return findings

def _detect_monitoring_software(family_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Detect device monitoring software and capabilities."""
    findings = []
    
    try:
        system = platform.system()
        detected_monitoring = []
        
        if system == "Windows":
            result = subprocess.run(['tasklist'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                processes = result.stdout.lower()
                monitoring_software = {
                    'spyrix': 'Spyrix Personal Monitor',
                    'kidlogger': 'KidLogger',
                    'refog': 'Refog Keylogger',
                    'mspy': 'mSpy',
                    'flexispy': 'FlexiSpy'
                }
                
                for pname, sname in monitoring_software.items():
                    if pname in processes:
                        detected_monitoring.append(sname)
        
        if detected_monitoring:
            findings.append(_create_finding(
                'info', 'Device Monitoring Software Detected',
                f'Found monitoring software: {", ".join(detected_monitoring)}',
                'Ensure monitoring software is used ethically and with family consent',
                {'detected_monitoring': detected_monitoring}
            ))
        else:
            findings.append(_create_finding(
                'info', 'No Monitoring Software Detected',
                'No device monitoring software detected',
                'Consider age-appropriate monitoring solutions if needed for family safety',
                {'detected_monitoring': []}
            ))
    except Exception as e:
        findings.append(_create_finding(
            'low', 'Monitoring Software Check Error',
            f'Unable to check for monitoring software: {str(e)}',
            'Manually review installed monitoring software',
            {'error': str(e)}
        ))
    
    return findings

def _check_screen_time_controls(family_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Check for screen time control settings."""
    findings = []
    
    try:
        system = platform.system()
        
        if system == "Windows":
            findings.append(_create_finding(
                'info', 'Windows Screen Time Controls',
                'Windows Family Safety includes screen time management',
                'Configure screen time limits through Microsoft Family accounts',
                {'platform': 'Windows', 'feature': 'Family Safety Screen Time'}
            ))
        elif system == "Darwin":
            findings.append(_create_finding(
                'info', 'macOS Screen Time',
                'macOS includes comprehensive Screen Time controls',
                'Configure Screen Time limits and app restrictions in System Preferences',
                {'platform': 'macOS', 'feature': 'Screen Time'}
            ))
        else:
            findings.append(_create_finding(
                'info', 'Screen Time Controls',
                'Check available screen time control options for your platform',
                'Many devices and platforms offer screen time management features',
                {'platform': system}
            ))
    except Exception as e:
        findings.append(_create_finding(
            'low', 'Screen Time Check Error',
            f'Unable to check screen time controls: {str(e)}',
            'Manually review screen time control settings',
            {'error': str(e)}
        ))
    
    return findings

def _get_age_appropriate_social_media_guidance(family_members: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Get age-appropriate social media privacy guidance."""
    findings = []
    
    try:
        for member in family_members:
            age_group = member.get('age_group', 'unknown')
            name = member.get('name', 'Family Member')
            
            if age_group == 'child':
                findings.append(_create_finding(
                    'high', f'Child Social Media Safety - {name}',
                    'Young children should have limited or no social media access',
                    'Consider age-appropriate alternatives and supervised usage only',
                    {'age_group': 'child', 'member': name}
                ))
            elif age_group == 'teen':
                findings.append(_create_finding(
                    'medium', f'Teen Social Media Privacy - {name}',
                    'Teenagers need guidance on social media privacy settings',
                    'Review privacy settings together and discuss online safety regularly',
                    {'age_group': 'teen', 'member': name}
                ))
            elif age_group == 'adult':
                findings.append(_create_finding(
                    'info', f'Adult Social Media Privacy - {name}',
                    'Adults should model good social media privacy practices',
                    'Regularly review and update privacy settings on all platforms',
                    {'age_group': 'adult', 'member': name}
                ))
    except Exception as e:
        findings.append(_create_finding(
            'low', 'Social Media Guidance Error',
            f'Unable to generate age-appropriate guidance: {str(e)}',
            'Manually review social media settings for all family members',
            {'error': str(e)}
        ))
    
    return findings

def _get_platform_privacy_recommendations() -> List[Dict[str, Any]]:
    """Get platform-specific privacy recommendations."""
    findings = []
    platforms = {
        'Facebook': 'Review privacy settings, limit data sharing, and use two-factor authentication',
        'Instagram': 'Set account to private, review story settings, and limit location sharing',
        'TikTok': 'Set account to private, disable location services, and review data sharing settings',
        'Snapchat': 'Enable Ghost Mode, review who can contact you, and limit location sharing',
        'Twitter': 'Review privacy settings, limit data sharing, and protect your tweets',
        'YouTube': 'Use Restricted Mode for children, review privacy settings, and manage watch history'
    }
    
    for platform_name, recommendation in platforms.items():
        findings.append(_create_finding(
            'info', f'{platform_name} Privacy Settings',
            f'Privacy recommendations for {platform_name}',
            recommendation,
            {'platform': platform_name}
        ))
    
    return findings

def _generate_parental_control_recommendations(findings: List[Dict[str, Any]], family_profile: Dict[str, Any]) -> List[str]:
    """Generate actionable parental control recommendations."""
    recommendations = [f['recommendation'] for f in findings if 'recommendation' in f]
    
    general_recs = [
        'Establish clear family rules for internet and device usage',
        'Use age-appropriate content filtering and monitoring tools',
        'Regularly discuss online safety with all family members',
        'Set up screen time limits and device-free zones',
        'Review and update privacy settings on all social media platforms',
        'Enable safe search on all search engines',
        'Use family-safe DNS filtering services',
        'Regularly review and update parental control software',
        'Create separate user accounts for children with appropriate restrictions',
        'Monitor and review online activity regularly but respectfully'
    ]
    
    for rec in general_recs:
        if all(rec.lower() not in r.lower() for r in recommendations):
            recommendations.append(rec)
    
    return recommendations[:15]

def _determine_overall_status(findings: List[Dict[str, Any]]) -> str:
    """Determine overall parental control status."""
    if not findings:
        return 'secure'
    
    critical = sum(1 for f in findings if f.get('severity', '').lower() == 'critical')
    high = sum(1 for f in findings if f.get('severity', '').lower() == 'high')
    medium = sum(1 for f in findings if f.get('severity', '').lower() == 'medium')
    
    if critical > 0 or high >= 2:
        return 'critical'
    if high > 0 or medium >= 3:
        return 'warning'
    if medium > 0:
        return 'warning'
    return 'secure'

def _create_finding(severity: str, title: str, description: str, 
                   recommendation: Optional[str] = None, technical_info: Optional[Dict] = None) -> Dict[str, Any]:
    """Helper to create a finding."""
    finding = {
        'severity': severity,
        'title': title,
        'description': description,
        'timestamp': datetime.now().isoformat()
    }
    
    if recommendation:
        finding['recommendation'] = recommendation
    if technical_info:
        finding['technical_info'] = technical_info
    
    return finding

class ParentalControlProtocol:
    """Parental Control Protocol class for object-oriented usage."""
    
    def __init__(self):
        self.name = "Parental Control Protocol"
        self.version = "1.0.0"
        self.author = "Guardian Team"
        self.description = "Comprehensive parental control system analysis"
        self.family_friendly = True
        self.supported_protocols = [
            'content_filtering', 
            'device_monitoring', 
            'time_restrictions', 
            'social_media_privacy'
        ]
    
    def analyze(self, target=None, **kwargs):
        return analyze(target, **kwargs)
    
    def get_metadata(self):
        return get_metadata()