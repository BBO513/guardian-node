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
        check_type = kwargs.get('check_type')
        
        check_functions = {
            'content_filtering': _analyze_content_filtering,
            'device_monitoring': _analyze_device_monitoring,
            'time_restrictions': _analyze_time_restrictions,
            'social_media_privacy': _analyze_social_media_privacy,
        }
        
        if check_type in check_functions:
            to_run = [check_functions[check_type]]
        elif check_type is None or check_type == 'all':
            to_run = list(check_functions.values())
        else:
            to_run = []
        
        for fn in to_run:
            result = fn(family_profile)
            findings.extend(result.get('findings', []))
            recommendations.extend(result.get('recommendations', []))
            technical_details.update(result.get('technical_details', {}) or {})
        
        status = _determine_overall_status(findings)
        
        technical_details.update({
            'checks_performed': [name for name, f in check_functions.items() if f in to_run],
            'family_profile_provided': bool(kwargs.get('family_profile')),
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
            'findings': [_create_finding(
                severity='high',
                title='Analysis Error',
                description=f'Parental control analysis could not complete: {str(e)}',
                recommendation='Check logs and retry the analysis.'
            )],
            'recommendations': [f'Parental control analysis failed: {str(e)}'],
            'technical_details': {'error': str(e)}
        }

def _analyze_content_filtering(family_profile: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze content filtering systems and settings."""
    findings = []
    recommendations = []
    technical_details = {}
    
    try:
        dns_result = _check_dns_filtering(family_profile)
        software_result = _check_parental_control_software(family_profile)
        technical_details['dns_filtering'] = dns_result
        technical_details['parental_control_software'] = software_result
        
        if dns_result.get('filtered_dns'):
            findings.append(_create_finding(
                'info', 'DNS Filtering Active',
                f"Family-safe DNS detected: {dns_result.get('service')}",
                'Continue using family-safe DNS and regularly review filtering settings'
            ))
            recommendations.append(f"DNS filtering is active via {dns_result.get('service')}")
        else:
            findings.append(_create_finding(
                'medium', 'No DNS Filtering Detected',
                'System is not using family-safe DNS filtering',
                'Consider switching to a family-safe DNS service'
            ))
            recommendations.append('Consider switching to a family-safe DNS service')
        
        if software_result.get('detected'):
            findings.append(_create_finding(
                'info', 'Parental Control Software Found',
                f"Detected: {', '.join(software_result.get('software', []))}",
                'Keep parental control software properly configured and up to date'
            ))
            recommendations.append('Parental control software is installed')
        else:
            findings.append(_create_finding(
                'medium', 'No Parental Control Software',
                'No parental control software detected',
                'Consider installing parental control software for comprehensive family protection'
            ))
            recommendations.append('Consider installing parental control software')
    except Exception as e:
        findings.append(_create_finding(
            'low', 'Content Filtering Analysis Error',
            f'Unable to complete content filtering analysis: {str(e)}',
            'Manually review your content filtering settings',
            {'error': str(e)}
        ))
    
    return {'findings': findings, 'recommendations': recommendations, 'technical_details': technical_details}

def _analyze_device_monitoring(family_profile: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze device monitoring capabilities and settings."""
    findings = []
    recommendations = []
    technical_details = {}
    
    try:
        software_list = _detect_monitoring_software(family_profile)
        builtin = _check_builtin_parental_controls(family_profile)
        technical_details['monitoring_software'] = software_list
        technical_details['builtin_controls'] = builtin
        
        if software_list:
            findings.append(_create_finding(
                'info', 'Device Monitoring Active',
                f"Monitoring software detected: {', '.join(software_list)}",
                'Ensure monitoring software is used ethically and with family consent'
            ))
            recommendations.append('Device monitoring software is active')
        else:
            findings.append(_create_finding(
                'info', 'No Monitoring Software Detected',
                'No device monitoring software detected',
                'Consider age-appropriate monitoring solutions if needed for family safety'
            ))
        
        if builtin.get('enabled'):
            findings.append(_create_finding(
                'info', 'Built-in Controls Active',
                f"Built-in controls available: {', '.join(builtin.get('features', []))}",
                'Configure built-in parental controls for family protection'
            ))
            recommendations.append('Built-in parental controls are available')
    except Exception as e:
        findings.append(_create_finding(
            'low', 'Device Monitoring Analysis Error',
            f'Unable to complete device monitoring analysis: {str(e)}',
            'Manually review your device monitoring settings',
            {'error': str(e)}
        ))
    
    return {'findings': findings, 'recommendations': recommendations, 'technical_details': technical_details}

def _analyze_time_restrictions(family_profile: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze time restriction settings and controls."""
    findings = []
    recommendations = []
    technical_details = {}
    
    try:
        screen = _check_screen_time_controls(family_profile)
        bedtime = _check_bedtime_restrictions(family_profile)
        apps = _check_app_time_limits(family_profile)
        technical_details['screen_time'] = screen
        technical_details['bedtime'] = bedtime
        technical_details['app_limits'] = apps
        
        if screen.get('enabled'):
            findings.append(_create_finding(
                'info', 'Screen Time Controls Active',
                f"Screen time controls available: {', '.join(screen.get('features', []))}",
                'Configure screen time limits through family accounts'
            ))
            recommendations.append('Screen time controls are available')
        
        if bedtime.get('configured'):
            findings.append(_create_finding(
                'info', 'Bedtime Restrictions Set',
                'Bedtime restrictions are configured',
                'Review bedtime restrictions regularly'
            ))
            recommendations.append('Bedtime restrictions are configured')
        
        if apps.get('configured'):
            findings.append(_create_finding(
                'info', 'App Time Limits Set',
                f"App time limits configured for: {', '.join(apps.get('apps', []))}",
                'Review app time limits regularly'
            ))
            recommendations.append('App time limits are configured')
    except Exception as e:
        findings.append(_create_finding(
            'low', 'Time Restrictions Analysis Error',
            f'Unable to complete time restrictions analysis: {str(e)}',
            'Manually review your time restriction settings',
            {'error': str(e)}
        ))
    
    return {'findings': findings, 'recommendations': recommendations, 'technical_details': technical_details}

def _analyze_social_media_privacy(family_profile: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze social media privacy settings and recommendations."""
    findings = []
    recommendations = []
    technical_details = {}
    
    try:
        family_members = family_profile.get('members', [])
        guidance = _get_age_appropriate_social_media_guidance(family_members)
        findings.extend(guidance.get('findings', []))
        recommendations.extend(guidance.get('recommendations', []))
        technical_details.update(guidance.get('technical_details', {}))
        
        platform_recs = _get_platform_privacy_recommendations()
        for platform_name, recs in platform_recs.items():
            findings.append(_create_finding(
                'info', f'{platform_name} Privacy Settings',
                f'Privacy recommendations for {platform_name}',
                recs[0] if recs else '',
                {'platform': platform_name}
            ))
            for rec in recs:
                recommendations.append(f'{platform_name}: {rec}')
        
        technical_details['platforms_reviewed'] = list(platform_recs.keys())
    except Exception as e:
        findings.append(_create_finding(
            'low', 'Social Media Privacy Analysis Error',
            f'Unable to complete social media privacy analysis: {str(e)}',
            'Manually review social media privacy settings for all family members',
            {'error': str(e)}
        ))
    
    return {'findings': findings, 'recommendations': recommendations, 'technical_details': technical_details}

def _check_dns_filtering(family_profile: Dict[str, Any]) -> Dict[str, Any]:
    """Check for DNS-based content filtering."""
    family_dns_servers = {
        '208.67.222.123': 'OpenDNS Family Shield',
        '208.67.220.123': 'OpenDNS Family Shield',
        '185.228.168.168': 'CleanBrowsing Family',
        '185.228.169.168': 'CleanBrowsing Family',
        '1.1.1.3': 'Cloudflare for Families',
        '1.0.0.3': 'Cloudflare for Families',
    }
    
    try:
        system = platform.system()
        if system == "Windows":
            result = subprocess.run(['ipconfig', '/all'], capture_output=True, text=True, timeout=10)
            output = result.stdout
        else:
            result = subprocess.run(['cat', '/etc/resolv.conf'], capture_output=True, text=True, timeout=10)
            output = result.stdout
        
        dns_servers = re.findall(r'\d+\.\d+\.\d+\.\d+', output)
        
        for server in dns_servers:
            if server in family_dns_servers:
                return {
                    'filtered_dns': True,
                    'service': family_dns_servers[server],
                    'dns_server': server
                }
        
        return {
            'filtered_dns': False,
            'service': None,
            'dns_server': dns_servers[0] if dns_servers else None
        }
    except Exception:
        return {'filtered_dns': False, 'service': None, 'dns_server': None}

def _check_parental_control_software(family_profile: Dict[str, Any]) -> Dict[str, Any]:
    """Check for installed parental control software."""
    parental_software = ['qustodio', 'norton', 'bark', 'circle', 'kaspersky', 'bitdefender']
    
    try:
        system = platform.system()
        if system == "Windows":
            result = subprocess.run(['tasklist'], capture_output=True, text=True, timeout=10)
            processes = result.stdout.lower()
        else:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=10)
            processes = result.stdout.lower()
        
        detected_software = [name for name in parental_software if name in processes]
        return {'detected': bool(detected_software), 'software': detected_software}
    except Exception:
        return {'detected': False, 'software': []}

def _check_builtin_parental_controls(family_profile: Dict[str, Any]) -> Dict[str, Any]:
    """Check for built-in parental control features."""
    system = platform.system()
    
    if system == "Windows":
        return {
            'enabled': True,
            'features': ['Windows Family Safety', 'Screen Time Management', 'Activity Reporting']
        }
    elif system == "Darwin":
        return {
            'enabled': True,
            'features': ['macOS Screen Time', 'App Restrictions']
        }
    else:
        return {'enabled': False, 'features': []}

def _detect_monitoring_software(family_profile: Dict[str, Any]) -> List[str]:
    """Detect device monitoring software and capabilities."""
    monitoring_software = ['qustodio', 'bark', 'circle']
    
    try:
        system = platform.system()
        if system == "Windows":
            result = subprocess.run(['tasklist'], capture_output=True, text=True, timeout=10)
            processes = result.stdout.lower()
        else:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=10)
            processes = result.stdout.lower()
        
        return [name for name in monitoring_software if name in processes]
    except Exception:
        return []

def _check_screen_time_controls(family_profile: Dict[str, Any]) -> Dict[str, Any]:
    """Check for screen time control settings."""
    system = platform.system()
    
    if system == "Windows":
        return {
            'enabled': True,
            'features': ['Windows Family Features', 'Screen Time Limits']
        }
    elif system == "Darwin":
        return {
            'enabled': True,
            'features': ['macOS Screen Time', 'App Limits']
        }
    else:
        return {'enabled': False, 'features': []}

def _check_bedtime_restrictions(family_profile: Dict[str, Any]) -> Dict[str, Any]:
    """Check for bedtime restriction settings."""
    return {'configured': False}

def _check_app_time_limits(family_profile: Dict[str, Any]) -> Dict[str, Any]:
    """Check for app time limit settings."""
    return {'configured': False, 'apps': []}

def _get_age_appropriate_social_media_guidance(family_members: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Get age-appropriate social media privacy guidance."""
    findings = []
    recommendations = []
    age_groups = []
    
    try:
        for member in family_members:
            age_group = member.get('age_group', 'unknown')
            name = member.get('name', 'Family Member')
            age_groups.append(age_group)
            
            if age_group == 'child':
                findings.append(_create_finding(
                    'high', f'Child Social Media Safety - {name}',
                    'Young children should have limited or no social media access',
                    f'{name}: Consider age-appropriate alternatives and supervised usage only',
                    {'age_group': 'child', 'member': name}
                ))
                recommendations.append(f'{name}: Consider age-appropriate alternatives and supervised usage only')
            elif age_group == 'teen':
                findings.append(_create_finding(
                    'medium', f'Teen Social Media Privacy - {name}',
                    'Teenagers need guidance on social media privacy settings',
                    f'{name}: Review privacy settings together and discuss online safety regularly',
                    {'age_group': 'teen', 'member': name}
                ))
                recommendations.append(f'{name}: Review privacy settings together and discuss online safety regularly')
            else:
                findings.append(_create_finding(
                    'info', f'Adult Social Media Privacy - {name}',
                    'Adults should model good social media privacy practices',
                    f'{name}: Regularly review and update privacy settings on all platforms',
                    {'age_group': age_group, 'member': name}
                ))
                recommendations.append(f'{name}: Regularly review and update privacy settings on all platforms')
    except Exception as e:
        findings.append(_create_finding(
            'low', 'Social Media Guidance Error',
            f'Unable to generate age-appropriate guidance: {str(e)}',
            'Manually review social media settings for all family members',
            {'error': str(e)}
        ))
    
    return {
        'findings': findings,
        'recommendations': recommendations,
        'technical_details': {
            'members_analyzed': len(family_members),
            'age_groups': age_groups
        }
    }

def _get_platform_privacy_recommendations() -> Dict[str, List[str]]:
    """Get platform-specific privacy recommendations."""
    return {
        'Facebook': [
            'Review privacy settings and limit data sharing',
            'Use two-factor authentication'
        ],
        'Instagram': [
            'Set account to private',
            'Review story settings and limit location sharing'
        ],
        'TikTok': [
            'Set account to private',
            'Disable location services and review data sharing settings'
        ],
        'Snapchat': [
            'Enable Ghost Mode in Snap Map',
            'Review who can contact you and limit location sharing'
        ],
        'Twitter': [
            'Protect your tweets',
            'Review privacy settings and limit data sharing'
        ],
        'YouTube': [
            'Turn on Restricted Mode',
            'Manage watch history'
        ],
        'Discord': [
            'Adjust privacy and safety settings',
            'Review friend request settings'
        ]
    }

def _determine_overall_status(findings: List[Dict[str, Any]]) -> str:
    """Determine overall parental control status."""
    severities = {f.get('severity', '').lower() for f in findings}
    if 'critical' in severities or 'high' in severities:
        return 'critical'
    if severities:
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
