"""
Threat Analysis Skill for Family Cybersecurity
Analyzes current cybersecurity threats relevant to families and provides
family-friendly explanations with prioritization based on family impact.
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import re

class ThreatDatabase:
    """Database of common cybersecurity threats relevant to families"""
    
    def __init__(self):
        self.threats = {
            'phishing': {
                'name': 'Phishing Attacks',
                'description': 'Fake emails, texts, or websites that try to steal your personal information',
                'family_impact': 'high',
                'likelihood': 'very_high',
                'examples': [
                    'Fake bank emails asking for account details',
                    'Text messages claiming you won a prize',
                    'Fake social media login pages'
                ],
                'prevention': [
                    'Always check the sender\'s email address carefully',
                    'Never click links in suspicious emails',
                    'Type website addresses directly into your browser',
                    'Look for spelling mistakes and poor grammar'
                ],
                'family_analogy': 'Like strangers calling pretending to be your bank to get your information'
            },
            'malware': {
                'name': 'Malicious Software',
                'description': 'Harmful programs that can damage your devices or steal information',
                'family_impact': 'high',
                'likelihood': 'high',
                'examples': [
                    'Computer viruses from infected downloads',
                    'Ransomware that locks your files',
                    'Spyware that watches what you do online'
                ],
                'prevention': [
                    'Install reputable antivirus software',
                    'Only download apps from official stores',
                    'Keep your devices updated',
                    'Be careful with email attachments'
                ],
                'family_analogy': 'Like germs that can make your devices "sick" and spread to other devices'
            },
            'social_engineering': {
                'name': 'Social Engineering',
                'description': 'Tricks that manipulate people into giving away information or access',
                'family_impact': 'high',
                'likelihood': 'high',
                'examples': [
                    'Phone calls pretending to be tech support',
                    'Fake emergency calls asking for money',
                    'Strangers asking for personal information online'
                ],
                'prevention': [
                    'Never give personal information to unsolicited callers',
                    'Verify identity through official channels',
                    'Teach children never to share personal details online',
                    'Be suspicious of urgent requests for information'
                ],
                'family_analogy': 'Like con artists who use tricks and lies to get what they want'
            },
            'weak_passwords': {
                'name': 'Weak Password Security',
                'description': 'Using easy-to-guess or repeated passwords across multiple accounts',
                'family_impact': 'very_high',
                'likelihood': 'very_high',
                'examples': [
                    'Using "password123" or "123456"',
                    'Using the same password for everything',
                    'Using personal information like birthdays'
                ],
                'prevention': [
                    'Use unique passwords for each account',
                    'Make passwords long and complex',
                    'Use a password manager',
                    'Enable two-factor authentication'
                ],
                'family_analogy': 'Like using the same key for your house, car, and office - if someone gets it, they can access everything'
            },
            'unsecured_wifi': {
                'name': 'Unsecured Wi-Fi Networks',
                'description': 'Using public or poorly secured wireless networks that can expose your data',
                'family_impact': 'medium',
                'likelihood': 'high',
                'examples': [
                    'Free Wi-Fi at coffee shops or airports',
                    'Home Wi-Fi without a password',
                    'Fake Wi-Fi hotspots set up by criminals'
                ],
                'prevention': [
                    'Avoid sensitive activities on public Wi-Fi',
                    'Use a VPN when on public networks',
                    'Secure your home Wi-Fi with a strong password',
                    'Turn off auto-connect to Wi-Fi networks'
                ],
                'family_analogy': 'Like having conversations in a crowded room where anyone can listen in'
            },
            'online_predators': {
                'name': 'Online Predators',
                'description': 'Adults who use the internet to harm or exploit children',
                'family_impact': 'very_high',
                'likelihood': 'medium',
                'examples': [
                    'Strangers trying to befriend children online',
                    'Requests for personal information or photos',
                    'Attempts to meet children in person'
                ],
                'prevention': [
                    'Monitor children\'s online activities',
                    'Teach children never to meet online friends in person',
                    'Use parental controls on devices',
                    'Have open conversations about online safety'
                ],
                'family_analogy': 'Like strangers who approach children in playgrounds, but online'
            },
            'cyberbullying': {
                'name': 'Cyberbullying',
                'description': 'Using technology to harass, threaten, or embarrass others',
                'family_impact': 'high',
                'likelihood': 'high',
                'examples': [
                    'Mean messages on social media',
                    'Sharing embarrassing photos without permission',
                    'Excluding someone from online groups'
                ],
                'prevention': [
                    'Teach children to be kind online',
                    'Report and block bullies',
                    'Save evidence of cyberbullying',
                    'Talk to children about their online experiences'
                ],
                'family_analogy': 'Like playground bullying, but it can follow children home through their devices'
            },
            'identity_theft': {
                'name': 'Identity Theft',
                'description': 'Criminals stealing personal information to pretend to be you',
                'family_impact': 'very_high',
                'likelihood': 'medium',
                'examples': [
                    'Using stolen credit card information',
                    'Opening accounts in your name',
                    'Filing fake tax returns'
                ],
                'prevention': [
                    'Protect Social Security numbers and personal documents',
                    'Monitor bank and credit card statements',
                    'Shred documents with personal information',
                    'Be careful what you share on social media'
                ],
                'family_analogy': 'Like someone stealing your wallet and pretending to be you'
            }
        }
    
    def get_threat(self, threat_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific threat"""
        return self.threats.get(threat_id.lower())
    
    def get_all_threats(self) -> Dict[str, Dict[str, Any]]:
        """Get all threats in the database"""
        return self.threats
    
    def search_threats(self, query: str) -> List[Tuple[str, Dict[str, Any]]]:
        """Search for threats based on a query"""
        query_lower = query.lower()
        matches = []
        
        for threat_id, threat_data in self.threats.items():
            # Check if query matches threat name, description, or examples
            if (query_lower in threat_data['name'].lower() or 
                query_lower in threat_data['description'].lower() or
                any(query_lower in example.lower() for example in threat_data['examples'])):
                matches.append((threat_id, threat_data))
        
        return matches

class ThreatPrioritizer:
    """Prioritizes threats based on family impact and likelihood"""
    
    @staticmethod
    def calculate_priority_score(threat: Dict[str, Any]) -> int:
        """Calculate a priority score for a threat"""
        impact_scores = {
            'very_high': 4,
            'high': 3,
            'medium': 2,
            'low': 1
        }
        
        likelihood_scores = {
            'very_high': 4,
            'high': 3,
            'medium': 2,
            'low': 1
        }
        
        impact = impact_scores.get(threat.get('family_impact', 'medium'), 2)
        likelihood = likelihood_scores.get(threat.get('likelihood', 'medium'), 2)
        
        # Priority score is impact * likelihood
        return impact * likelihood
    
    @staticmethod
    def prioritize_threats(threats: List[Tuple[str, Dict[str, Any]]]) -> List[Tuple[str, Dict[str, Any], int]]:
        """Sort threats by priority score"""
        prioritized = []
        for threat_id, threat_data in threats:
            score = ThreatPrioritizer.calculate_priority_score(threat_data)
            prioritized.append((threat_id, threat_data, score))
        
        # Sort by score (highest first)
        return sorted(prioritized, key=lambda x: x[2], reverse=True)

class FamilyThreatExplainer:
    """Formats threat information in family-friendly language"""
    
    @staticmethod
    def format_threat_explanation(threat_id: str, threat_data: Dict[str, Any], include_examples: bool = True) -> str:
        """Format a complete threat explanation for families"""
        explanation = f"🚨 **{threat_data['name']}**\n\n"
        
        # Description
        explanation += f"**What it is:** {threat_data['description']}\n\n"
        
        # Family analogy
        if 'family_analogy' in threat_data:
            explanation += f"💡 **Think of it like:** {threat_data['family_analogy']}\n\n"
        
        # Examples (if requested)
        if include_examples and threat_data.get('examples'):
            explanation += "**Common examples:**\n"
            for example in threat_data['examples']:
                explanation += f"• {example}\n"
            explanation += "\n"
        
        # Prevention tips
        if threat_data.get('prevention'):
            explanation += "🛡️ **How to protect your family:**\n"
            for tip in threat_data['prevention']:
                explanation += f"• {tip}\n"
            explanation += "\n"
        
        # Priority indicator
        impact = threat_data.get('family_impact', 'medium')
        likelihood = threat_data.get('likelihood', 'medium')
        
        priority_emoji = {
            'very_high': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢'
        }
        
        explanation += f"**Priority Level:** {priority_emoji.get(impact, '🟡')} "
        explanation += f"Impact: {impact.replace('_', ' ').title()}, "
        explanation += f"Likelihood: {likelihood.replace('_', ' ').title()}"
        
        return explanation
    
    @staticmethod
    def format_threat_summary(threats: List[Tuple[str, Dict[str, Any], int]]) -> str:
        """Format a summary of multiple threats"""
        if not threats:
            return "No specific threats found for your query."
        
        summary = "🔍 **Cybersecurity Threats for Your Family**\n\n"
        
        for i, (threat_id, threat_data, score) in enumerate(threats[:5], 1):  # Limit to top 5
            priority_emoji = '🔴' if score >= 12 else '🟠' if score >= 8 else '🟡' if score >= 4 else '🟢'
            summary += f"{priority_emoji} **{i}. {threat_data['name']}**\n"
            summary += f"   {threat_data['description']}\n\n"
        
        if len(threats) > 5:
            summary += f"... and {len(threats) - 5} more threats.\n\n"
        
        summary += "💡 Ask me about any specific threat for detailed protection advice!"
        
        return summary

class ThreatAnalysisSkill:
    """Main threat analysis skill class"""
    
    def __init__(self):
        self.threat_db = ThreatDatabase()
        self.prioritizer = ThreatPrioritizer()
        self.explainer = FamilyThreatExplainer()
    
    def analyze_general_threats(self) -> str:
        """Provide general threat analysis for families"""
        all_threats = list(self.threat_db.get_all_threats().items())
        prioritized = self.prioritizer.prioritize_threats(all_threats)
        
        return self.explainer.format_threat_summary(prioritized)
    
    def analyze_specific_threat(self, threat_query: str) -> str:
        """Analyze a specific threat based on user query"""
        # First try to find exact match
        threat_data = self.threat_db.get_threat(threat_query)
        if threat_data:
            return self.explainer.format_threat_explanation(threat_query, threat_data)
        
        # If no exact match, search for related threats
        matches = self.threat_db.search_threats(threat_query)
        if matches:
            if len(matches) == 1:
                threat_id, threat_data = matches[0]
                return self.explainer.format_threat_explanation(threat_id, threat_data)
            else:
                prioritized = self.prioritizer.prioritize_threats(matches)
                return self.explainer.format_threat_summary(prioritized)
        
        # No matches found
        return f"I couldn't find specific information about '{threat_query}'. " \
               f"Try asking about common threats like 'phishing', 'malware', 'passwords', or 'online safety'."
    
    def get_current_threat_landscape(self) -> str:
        """Provide current threat landscape overview"""
        response = "🌐 **Current Cybersecurity Landscape for Families**\n\n"
        
        # Get top threats by priority
        all_threats = list(self.threat_db.get_all_threats().items())
        prioritized = self.prioritizer.prioritize_threats(all_threats)
        top_threats = prioritized[:3]
        
        response += "**Top 3 Threats to Watch:**\n\n"
        
        for i, (threat_id, threat_data, score) in enumerate(top_threats, 1):
            response += f"**{i}. {threat_data['name']}**\n"
            response += f"   Why it matters: {threat_data['description']}\n"
            response += f"   Quick tip: {threat_data['prevention'][0]}\n\n"
        
        response += "💡 **Remember:** Most cyber threats can be prevented with good habits and awareness!\n\n"
        response += "Ask me about any specific threat for detailed protection strategies."
        
        return response

def run(*args, **kwargs):
    """
    Main entry point for threat analysis skill
    
    Args:
        *args: Query and additional arguments
        **kwargs: Additional context
    
    Returns:
        str: Threat analysis and family-friendly recommendations
    """
    try:
        threat_analyzer = ThreatAnalysisSkill()
        
        # Handle case where no query is provided
        if not args:
            return threat_analyzer.get_current_threat_landscape()
        
        # Get the query
        query = " ".join(args).strip()
        
        # Handle different types of queries
        if any(word in query.lower() for word in ['current', 'latest', 'today', 'now', 'landscape']):
            return threat_analyzer.get_current_threat_landscape()
        elif any(word in query.lower() for word in ['all', 'general', 'overview', 'summary']):
            return threat_analyzer.analyze_general_threats()
        else:
            # Specific threat query
            return threat_analyzer.analyze_specific_threat(query)
    
    except Exception as e:
        # Graceful error handling
        error_response = "I'm sorry, I encountered an issue while analyzing cybersecurity threats. "
        error_response += "Please try asking about specific threats like 'phishing', 'malware', or 'password security'."
        
        # Log the error for debugging
        print(f"Threat Analysis Skill Error: {e}")
        
        return error_response

# Skill metadata
__doc__ = "Analyzes cybersecurity threats relevant to families with prioritization and family-friendly explanations"
__version__ = "1.0.0"
__author__ = "Guardian Family Assistant"
__category__ = "threat_analysis"