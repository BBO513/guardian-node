"""
Family Cybersecurity Skills - Main Router
This skill serves as the main entry point for family cybersecurity assistance.
It routes queries to specialized sub-skills and formats responses in family-friendly language.
"""

import re
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

class FamilyResponseFormatter:
    """Handles formatting technical responses into family-friendly language"""
    
    @staticmethod
    def simplify_technical_terms(text: str) -> str:
        """Replace technical jargon with family-friendly explanations"""
        replacements = {
            'malware': 'harmful software',
            'phishing': 'fake emails trying to steal information',
            'ransomware': 'software that locks your files for money',
            'firewall': 'digital security barrier',
            'encryption': 'scrambling data to keep it safe',
            'two-factor authentication': 'double-checking your identity',
            '2FA': 'double-checking your identity',
            'VPN': 'private internet tunnel',
            'router': 'internet box',
            'Wi-Fi': 'wireless internet',
            'password manager': 'secure password keeper',
            'antivirus': 'protection software',
            'operating system': 'device software',
            'browser': 'internet app',
            'cookies': 'website memory files',
            'cache': 'stored website data',
            'IP address': 'device internet address',
            'DNS': 'internet phone book',
            'SSL/TLS': 'secure connection',
            'HTTPS': 'secure website connection'
        }
        
        result = text
        for technical, simple in replacements.items():
            # Case-insensitive replacement
            pattern = re.compile(re.escape(technical), re.IGNORECASE)
            result = pattern.sub(simple, result)
        
        return result
    
    @staticmethod
    def add_family_analogies(text: str, topic: str) -> str:
        """Add helpful analogies based on the topic"""
        analogies = {
            'password': "Think of passwords like house keys - you wouldn't use the same key for your house, car, and office!",
            'firewall': "A firewall is like a security guard at your home - it checks who's trying to get in.",
            'backup': "Backing up files is like making photocopies of important documents and storing them safely.",
            'update': "Software updates are like getting your car serviced - they fix problems and keep things running smoothly.",
            'phishing': "Phishing emails are like strangers calling and pretending to be your bank to get your information.",
            'malware': "Malware is like germs - it can spread and make your devices 'sick' if you're not careful."
        }
        
        for key, analogy in analogies.items():
            if key.lower() in text.lower():
                text += f"\n\n💡 Think of it this way: {analogy}"
                break
        
        return text
    
    @staticmethod
    def format_for_family(response: str, context: Dict[str, Any] = None) -> str:
        """Main formatting function for family-friendly responses"""
        if not response:
            return "I'm sorry, I couldn't generate a helpful response right now."
        
        # Simplify technical terms
        formatted = FamilyResponseFormatter.simplify_technical_terms(response)
        
        # Add analogies if context is provided
        if context and 'topic' in context:
            formatted = FamilyResponseFormatter.add_family_analogies(formatted, context['topic'])
        
        # Add encouraging tone
        if not formatted.startswith(('Great', 'Good', 'Excellent', 'Nice')):
            formatted = f"Great question! {formatted}"
        
        # Add action-oriented ending if it's a recommendation
        if context and context.get('type') == 'recommendation':
            formatted += "\n\n✅ Would you like me to break this down into step-by-step instructions?"
        
        return formatted

class FamilyCyberSkills:
    """Main family cybersecurity skills coordinator"""
    
    def __init__(self):
        self.formatter = FamilyResponseFormatter()
        self.skill_categories = {
            'threats': ['threat', 'attack', 'virus', 'malware', 'scam', 'hack', 'danger', 'risk'],
            'devices': ['phone', 'tablet', 'computer', 'laptop', 'smart', 'device', 'router', 'wifi'],
            'education': ['child', 'kid', 'teen', 'teach', 'learn', 'explain', 'safe', 'safety'],
            'passwords': ['password', 'login', 'account', 'sign in', 'authentication'],
            'privacy': ['privacy', 'personal', 'data', 'information', 'share', 'social media'],
            'general': ['help', 'security', 'protect', 'safe', 'cyber', 'internet', 'online']
        }
    
    def categorize_query(self, query: str) -> str:
        """Determine which category a query belongs to"""
        query_lower = query.lower()
        
        # Count matches for each category
        category_scores = {}
        for category, keywords in self.skill_categories.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                category_scores[category] = score
        
        # Return category with highest score, or 'general' if no matches
        if category_scores:
            return max(category_scores, key=category_scores.get)
        return 'general'
    
    def route_to_subskill(self, query: str, category: str, *args) -> str:
        """Route query to appropriate sub-skill (placeholder for now)"""
        # This will be implemented when sub-skills are created
        responses = {
            'threats': f"I understand you're asking about cybersecurity threats. This is important for keeping your family safe online! Currently, I'm being enhanced with specialized threat analysis capabilities.",
            'devices': f"Device security is crucial for family safety! I'm being equipped with comprehensive device guidance features to help you secure all your family's devices.",
            'education': f"Teaching children about cybersecurity is so important! I'm developing specialized educational content and activities to help parents guide their kids safely online.",
            'passwords': f"Password security is fundamental! Here's what I can tell you: Use unique, strong passwords for each account, consider a password manager, and enable two-factor authentication where possible.",
            'privacy': f"Privacy protection is essential for families! I'm being enhanced with privacy guidance features to help you protect your family's personal information online.",
            'general': f"I'm here to help with your family's cybersecurity needs! I'm currently being enhanced with specialized skills for threat analysis, device guidance, and child education."
        }
        
        base_response = responses.get(category, responses['general'])
        
        # Add specific context based on the query
        context = {
            'topic': category,
            'type': 'guidance' if any(word in query.lower() for word in ['how', 'what', 'help']) else 'information'
        }
        
        return self.formatter.format_for_family(base_response, context)
    
    def get_family_recommendations(self, family_context: Dict[str, Any] = None) -> List[str]:
        """Generate basic family cybersecurity recommendations"""
        basic_recommendations = [
            "🔐 Use strong, unique passwords for all accounts",
            "📱 Keep all devices updated with the latest software",
            "🛡️ Install reputable antivirus software on computers",
            "🔒 Enable two-factor authentication on important accounts",
            "👨‍👩‍👧‍👦 Have regular family conversations about online safety",
            "📧 Be cautious with emails from unknown senders",
            "🏠 Secure your home Wi-Fi network with a strong password",
            "💾 Regularly backup important family photos and documents"
        ]
        
        return basic_recommendations
    
    def handle_emergency_query(self, query: str) -> Optional[str]:
        """Handle urgent cybersecurity concerns"""
        emergency_keywords = ['hacked', 'stolen', 'compromised', 'emergency', 'urgent', 'help', 'attacked']
        
        if any(keyword in query.lower() for keyword in emergency_keywords):
            return """🚨 If you believe your accounts or devices have been compromised:

1. **Immediate Steps:**
   - Disconnect the affected device from the internet
   - Change passwords for important accounts from a secure device
   - Contact your bank if financial accounts might be affected

2. **Next Steps:**
   - Run a full antivirus scan
   - Check recent account activity
   - Enable two-factor authentication
   - Consider contacting local authorities if identity theft is suspected

3. **Prevention:**
   - I can help you set up better security measures once the immediate issue is resolved

Stay calm - most cybersecurity issues can be resolved with the right steps!"""
        
        return None

def run(*args, **kwargs):
    """
    Main entry point for family cybersecurity skills
    
    Args:
        *args: Query and additional arguments
        **kwargs: Additional context (future use)
    
    Returns:
        str: Family-friendly cybersecurity guidance
    """
    try:
        # Initialize the family cyber skills system
        family_skills = FamilyCyberSkills()
        
        # Handle case where no query is provided
        if not args:
            recommendations = family_skills.get_family_recommendations()
            response = "👨‍👩‍👧‍👦 **Family Cybersecurity Assistant Ready!**\n\n"
            response += "Here are some essential cybersecurity tips for your family:\n\n"
            response += "\n".join(recommendations)
            response += "\n\n💬 Ask me specific questions about cybersecurity, device safety, or online protection!"
            return response
        
        # Get the main query
        query = " ".join(args)
        
        # Check for emergency situations first
        emergency_response = family_skills.handle_emergency_query(query)
        if emergency_response:
            return emergency_response
        
        # Categorize and route the query
        category = family_skills.categorize_query(query)
        response = family_skills.route_to_subskill(query, category, *args)
        
        # Add helpful footer
        response += "\n\n💡 **Tip:** I'm continuously being enhanced with more specialized family cybersecurity features!"
        
        return response
        
    except Exception as e:
        # Graceful error handling with family-friendly message
        error_response = "I'm sorry, I encountered an issue while processing your request. "
        error_response += "Please try rephrasing your question, and I'll do my best to help keep your family safe online!"
        
        # Log the actual error for debugging (would be handled by Guardian's logging system)
        print(f"Family Cyber Skills Error: {e}")
        
        return error_response

# Skill metadata
__doc__ = "Family-friendly cybersecurity assistance and guidance"
__version__ = "1.0.0"
__author__ = "Guardian Family Assistant"
__category__ = "family_security"