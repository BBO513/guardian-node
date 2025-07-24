"""
Device Guidance Skill for Family Cybersecurity
Provides security guidance for common family devices including phones, tablets, 
computers, and smart home devices with age-appropriate recommendations.
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import re

class DeviceSecurityDatabase:
    """Database of security guidance for different device types"""
    
    def __init__(self):
        self.devices = {
            'smartphone': {
                'name': 'Smartphones (iPhone/Android)',
                'common_names': ['phone', 'iphone', 'android', 'mobile', 'cell phone'],
                'security_features': {
                    'screen_lock': {
                        'name': 'Screen Lock',
                        'description': 'Password, PIN, fingerprint, or face unlock',
                        'importance': 'critical',
                        'setup_difficulty': 'easy'
                    },
                    'app_permissions': {
                        'name': 'App Permissions',
                        'description': 'Control what apps can access (camera, location, contacts)',
                        'importance': 'high',
                        'setup_difficulty': 'moderate'
                    },
                    'automatic_updates': {
                        'name': 'Automatic Updates',
                        'description': 'Keep the phone software up to date',
                        'importance': 'high',
                        'setup_difficulty': 'easy'
                    },
                    'find_my_device': {
                        'name': 'Find My Device',
                        'description': 'Locate, lock, or wipe your phone if lost',
                        'importance': 'high',
                        'setup_difficulty': 'moderate'
                    }
                },
                'age_specific': {
                    'child': [
                        'Set up parental controls',
                        'Limit app downloads to parent approval',
                        'Enable location sharing with parents',
                        'Set screen time limits'
                    ],
                    'teen': [
                        'Discuss privacy settings together',
                        'Enable location sharing for safety',
                        'Review social media privacy settings',
                        'Set up emergency contacts'
                    ],
                    'adult': [
                        'Use strong authentication methods',
                        'Review app permissions regularly',
                        'Enable two-factor authentication',
                        'Keep personal information private'
                    ]
                }
            },
            'tablet': {
                'name': 'Tablets (iPad/Android)',
                'common_names': ['tablet', 'ipad', 'android tablet'],
                'security_features': {
                    'screen_lock': {
                        'name': 'Screen Lock',
                        'description': 'Password, PIN, or biometric unlock',
                        'importance': 'critical',
                        'setup_difficulty': 'easy'
                    },
                    'app_store_restrictions': {
                        'name': 'App Store Restrictions',
                        'description': 'Control what apps can be downloaded',
                        'importance': 'high',
                        'setup_difficulty': 'moderate'
                    },
                    'content_filtering': {
                        'name': 'Content Filtering',
                        'description': 'Block inappropriate websites and content',
                        'importance': 'high',
                        'setup_difficulty': 'moderate'
                    }
                },
                'age_specific': {
                    'child': [
                        'Set up strong parental controls',
                        'Create a child-safe user profile',
                        'Enable content filtering',
                        'Limit screen time and app usage'
                    ],
                    'teen': [
                        'Review privacy settings together',
                        'Discuss appropriate app usage',
                        'Set reasonable time limits',
                        'Monitor social media activity'
                    ],
                    'adult': [
                        'Use secure authentication',
                        'Keep software updated',
                        'Be cautious with public Wi-Fi',
                        'Review app permissions'
                    ]
                }
            },
            'computer': {
                'name': 'Computers (Windows/Mac/Linux)',
                'common_names': ['computer', 'laptop', 'desktop', 'pc', 'mac'],
                'security_features': {
                    'antivirus': {
                        'name': 'Antivirus Software',
                        'description': 'Protection against malware and viruses',
                        'importance': 'critical',
                        'setup_difficulty': 'easy'
                    },
                    'firewall': {
                        'name': 'Firewall',
                        'description': 'Blocks unauthorized network access',
                        'importance': 'high',
                        'setup_difficulty': 'moderate'
                    },
                    'user_accounts': {
                        'name': 'User Accounts',
                        'description': 'Separate accounts for different family members',
                        'importance': 'high',
                        'setup_difficulty': 'moderate'
                    },
                    'automatic_updates': {
                        'name': 'Automatic Updates',
                        'description': 'Keep operating system and software updated',
                        'importance': 'critical',
                        'setup_difficulty': 'easy'
                    }
                },
                'age_specific': {
                    'child': [
                        'Create a limited user account (not administrator)',
                        'Install parental control software',
                        'Set up content filtering',
                        'Monitor computer usage time'
                    ],
                    'teen': [
                        'Teach safe browsing habits',
                        'Set up separate user account',
                        'Discuss online privacy',
                        'Monitor social media usage'
                    ],
                    'adult': [
                        'Use administrator account responsibly',
                        'Keep all software updated',
                        'Use strong passwords',
                        'Regular security scans'
                    ]
                }
            },
            'smart_home': {
                'name': 'Smart Home Devices',
                'common_names': ['smart home', 'alexa', 'google home', 'smart speaker', 'iot', 'smart tv'],
                'security_features': {
                    'default_passwords': {
                        'name': 'Change Default Passwords',
                        'description': 'Replace factory passwords with strong ones',
                        'importance': 'critical',
                        'setup_difficulty': 'moderate'
                    },
                    'network_segmentation': {
                        'name': 'Network Segmentation',
                        'description': 'Put smart devices on separate network',
                        'importance': 'high',
                        'setup_difficulty': 'advanced'
                    },
                    'privacy_settings': {
                        'name': 'Privacy Settings',
                        'description': 'Control data collection and sharing',
                        'importance': 'high',
                        'setup_difficulty': 'moderate'
                    },
                    'regular_updates': {
                        'name': 'Regular Updates',
                        'description': 'Keep device firmware updated',
                        'importance': 'high',
                        'setup_difficulty': 'easy'
                    }
                },
                'age_specific': {
                    'child': [
                        'Set up voice recognition for children',
                        'Enable parental controls',
                        'Limit purchasing capabilities',
                        'Monitor what children ask devices'
                    ],
                    'teen': [
                        'Discuss privacy implications',
                        'Set up individual profiles',
                        'Review data sharing settings',
                        'Teach responsible usage'
                    ],
                    'adult': [
                        'Review all privacy settings',
                        'Understand data collection',
                        'Secure network properly',
                        'Regular security audits'
                    ]
                }
            },
            'router': {
                'name': 'Home Router/Wi-Fi',
                'common_names': ['router', 'wifi', 'wi-fi', 'internet', 'modem'],
                'security_features': {
                    'admin_password': {
                        'name': 'Admin Password',
                        'description': 'Strong password for router administration',
                        'importance': 'critical',
                        'setup_difficulty': 'moderate'
                    },
                    'wifi_password': {
                        'name': 'Wi-Fi Password',
                        'description': 'Strong password for network access',
                        'importance': 'critical',
                        'setup_difficulty': 'easy'
                    },
                    'encryption': {
                        'name': 'WPA3 Encryption',
                        'description': 'Latest security protocol for Wi-Fi',
                        'importance': 'critical',
                        'setup_difficulty': 'moderate'
                    },
                    'guest_network': {
                        'name': 'Guest Network',
                        'description': 'Separate network for visitors',
                        'importance': 'medium',
                        'setup_difficulty': 'moderate'
                    }
                },
                'age_specific': {
                    'child': [
                        'Set up content filtering',
                        'Configure time-based access controls',
                        'Monitor internet usage',
                        'Block inappropriate websites'
                    ],
                    'teen': [
                        'Set reasonable time limits',
                        'Monitor but respect privacy',
                        'Discuss appropriate usage',
                        'Block dangerous websites'
                    ],
                    'adult': [
                        'Secure all network settings',
                        'Regular firmware updates',
                        'Monitor network activity',
                        'Configure advanced security features'
                    ]
                }
            }
        }
    
    def get_device(self, device_query: str) -> Optional[Dict[str, Any]]:
        """Get device information based on query"""
        query_lower = device_query.lower()
        
        for device_id, device_data in self.devices.items():
            if (device_id in query_lower or 
                any(name in query_lower for name in device_data['common_names'])):
                return {**device_data, 'device_id': device_id}
        
        return None
    
    def search_devices(self, query: str) -> List[Tuple[str, Dict[str, Any]]]:
        """Search for devices based on query"""
        query_lower = query.lower()
        matches = []
        
        for device_id, device_data in self.devices.items():
            if (query_lower in device_data['name'].lower() or
                any(query_lower in name for name in device_data['common_names'])):
                matches.append((device_id, device_data))
        
        return matches

class DeviceSecurityFormatter:
    """Formats device security guidance in family-friendly language"""
    
    @staticmethod
    def format_device_overview(device_data: Dict[str, Any]) -> str:
        """Format a complete device security overview"""
        overview = f"🔒 **{device_data['name']} Security Guide**\n\n"
        
        # Security features
        overview += "**Essential Security Features:**\n\n"
        
        for feature_id, feature in device_data['security_features'].items():
            importance_emoji = {
                'critical': '🔴',
                'high': '🟠',
                'medium': '🟡',
                'low': '🟢'
            }
            
            difficulty_emoji = {
                'easy': '✅',
                'moderate': '⚠️',
                'advanced': '🔧'
            }
            
            overview += f"{importance_emoji.get(feature['importance'], '🟡')} **{feature['name']}** "
            overview += f"{difficulty_emoji.get(feature['setup_difficulty'], '⚠️')}\n"
            overview += f"   {feature['description']}\n\n"
        
        return overview
    
    @staticmethod
    def format_age_specific_guidance(device_data: Dict[str, Any], age_group: str = None) -> str:
        """Format age-specific guidance"""
        if not device_data.get('age_specific'):
            return ""
        
        guidance = "👨‍👩‍👧‍👦 **Family-Specific Recommendations:**\n\n"
        
        if age_group and age_group in device_data['age_specific']:
            # Show specific age group
            guidance += f"**For {age_group.title()}s:**\n"
            for tip in device_data['age_specific'][age_group]:
                guidance += f"• {tip}\n"
            guidance += "\n"
        else:
            # Show all age groups
            for age, tips in device_data['age_specific'].items():
                guidance += f"**For {age.title()}s:**\n"
                for tip in tips:
                    guidance += f"• {tip}\n"
                guidance += "\n"
        
        return guidance
    
    @staticmethod
    def format_quick_setup_guide(device_data: Dict[str, Any]) -> str:
        """Format a quick setup guide with priorities"""
        guide = "🚀 **Quick Setup Priority List:**\n\n"
        
        # Sort features by importance
        features = device_data['security_features']
        sorted_features = sorted(features.items(), 
                               key=lambda x: {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
                               .get(x[1]['importance'], 1), reverse=True)
        
        for i, (feature_id, feature) in enumerate(sorted_features, 1):
            guide += f"**{i}. {feature['name']}**\n"
            guide += f"   {feature['description']}\n"
            
            difficulty = feature['setup_difficulty']
            if difficulty == 'easy':
                guide += "   ✅ Easy to set up - do this first!\n"
            elif difficulty == 'moderate':
                guide += "   ⚠️ Moderate setup - may need some help\n"
            else:
                guide += "   🔧 Advanced setup - consider getting technical help\n"
            guide += "\n"
        
        return guide

class DeviceGuidanceSkill:
    """Main device guidance skill class"""
    
    def __init__(self):
        self.device_db = DeviceSecurityDatabase()
        self.formatter = DeviceSecurityFormatter()
    
    def get_device_guidance(self, device_query: str, age_group: str = None) -> str:
        """Get comprehensive device security guidance"""
        device_data = self.device_db.get_device(device_query)
        
        if not device_data:
            # Try searching for partial matches
            matches = self.device_db.search_devices(device_query)
            if matches:
                if len(matches) == 1:
                    device_data = {**matches[0][1], 'device_id': matches[0][0]}
                else:
                    return self._format_device_options(matches)
            else:
                return self._format_device_not_found(device_query)
        
        # Format complete guidance
        guidance = self.formatter.format_device_overview(device_data)
        guidance += self.formatter.format_age_specific_guidance(device_data, age_group)
        guidance += self.formatter.format_quick_setup_guide(device_data)
        
        # Add helpful footer
        guidance += "💡 **Need help with setup?** Ask me for step-by-step instructions for any of these features!"
        
        return guidance
    
    def get_general_device_security(self) -> str:
        """Get general device security overview"""
        overview = "🔒 **Family Device Security Overview**\n\n"
        overview += "Here are the most important devices to secure in your home:\n\n"
        
        for device_id, device_data in self.device_db.devices.items():
            overview += f"📱 **{device_data['name']}**\n"
            
            # Get top 2 most important features
            features = device_data['security_features']
            critical_features = [f for f in features.values() if f['importance'] == 'critical']
            high_features = [f for f in features.values() if f['importance'] == 'high']
            
            top_features = critical_features[:2] + high_features[:2-len(critical_features)]
            
            for feature in top_features[:2]:
                overview += f"   • {feature['name']}: {feature['description']}\n"
            overview += "\n"
        
        overview += "💡 **Ask me about any specific device for detailed security guidance!**"
        
        return overview
    
    def _format_device_options(self, matches: List[Tuple[str, Dict[str, Any]]]) -> str:
        """Format multiple device options"""
        response = "I found several devices that might match your query:\n\n"
        
        for i, (device_id, device_data) in enumerate(matches, 1):
            response += f"{i}. **{device_data['name']}**\n"
        
        response += "\nPlease ask about a specific device type for detailed guidance!"
        
        return response
    
    def _format_device_not_found(self, query: str) -> str:
        """Format response when device is not found"""
        response = f"I couldn't find specific guidance for '{query}'. "
        response += "I can help with these device types:\n\n"
        
        for device_data in self.device_db.devices.values():
            response += f"• {device_data['name']}\n"
        
        response += "\nPlease ask about one of these device types!"
        
        return response

def run(*args, **kwargs):
    """
    Main entry point for device guidance skill
    
    Args:
        *args: Device query and additional arguments
        **kwargs: Additional context (age_group, etc.)
    
    Returns:
        str: Device security guidance
    """
    try:
        device_guidance = DeviceGuidanceSkill()
        
        # Handle case where no query is provided
        if not args:
            return device_guidance.get_general_device_security()
        
        # Parse arguments
        query = " ".join(args).strip()
        age_group = kwargs.get('age_group')
        
        # Check for age group in the query
        age_keywords = {
            'child': ['child', 'kid', 'young', 'elementary'],
            'teen': ['teen', 'teenager', 'adolescent', 'high school'],
            'adult': ['adult', 'parent', 'grown up']
        }
        
        if not age_group:
            for age, keywords in age_keywords.items():
                if any(keyword in query.lower() for keyword in keywords):
                    age_group = age
                    # Remove age keywords from query
                    for keyword in keywords:
                        query = re.sub(rf'\b{keyword}\b', '', query, flags=re.IGNORECASE)
                    query = query.strip()
                    break
        
        # Handle general queries
        if any(word in query.lower() for word in ['all', 'general', 'overview', 'summary']):
            return device_guidance.get_general_device_security()
        
        # Get specific device guidance
        return device_guidance.get_device_guidance(query, age_group)
    
    except Exception as e:
        # Graceful error handling
        error_response = "I'm sorry, I encountered an issue while providing device security guidance. "
        error_response += "Please try asking about specific devices like 'smartphone', 'computer', or 'router'."
        
        # Log the error for debugging
        print(f"Device Guidance Skill Error: {e}")
        
        return error_response

# Skill metadata
__doc__ = "Provides security guidance for common family devices with age-appropriate recommendations"
__version__ = "1.0.0"
__author__ = "Guardian Family Assistant"
__category__ = "device_security"