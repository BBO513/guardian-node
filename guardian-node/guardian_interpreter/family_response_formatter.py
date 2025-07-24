"""
Family Response Formatter for Guardian Node
Converts technical cybersecurity responses into family-friendly explanations.
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum
import re


class ComplexityLevel(Enum):
    """Response complexity levels"""
    SIMPLE = "simple"        # Very basic explanations
    MODERATE = "moderate"    # Balanced technical and simple
    DETAILED = "detailed"    # More comprehensive explanations


class ResponseLength(Enum):
    """Response length controls"""
    SHORT = "short"      # Brief, concise responses
    MEDIUM = "medium"    # Standard length responses
    LONG = "long"        # Detailed, comprehensive responses


class FamilyResponseFormatter:
    """
    Formats technical cybersecurity responses for family consumption
    """
    
    def __init__(self):
        self.technical_terms = self._initialize_technical_terms()
        self.analogies = self._initialize_analogies()
        self.complexity_modifiers = self._initialize_complexity_modifiers()
    
    def format_response(self, 
                       technical_response: str,
                       complexity_level: ComplexityLevel = ComplexityLevel.MODERATE,
                       response_length: ResponseLength = ResponseLength.MEDIUM,
                       target_age_group: Optional[str] = None) -> str:
        """
        Convert technical response to family-friendly format
        
        Args:
            technical_response: Original technical response
            complexity_level: Target complexity level
            response_length: Desired response length
            target_age_group: Optional age group (child, teen, adult)
            
        Returns:
            str: Formatted family-friendly response
        """
        # Start with the original response
        formatted = technical_response
        
        # Add analogies for complex concepts BEFORE replacing terms
        formatted = self._add_analogies(formatted, target_age_group)
        
        # Replace technical terms with family-friendly alternatives
        formatted = self._replace_technical_terms(formatted, complexity_level)
        
        # Adjust complexity based on level
        formatted = self._adjust_complexity(formatted, complexity_level)
        
        # Control response length
        formatted = self._control_length(formatted, response_length)
        
        # Add encouraging tone
        formatted = self._add_encouraging_tone(formatted)
        
        return formatted
    
    def _replace_technical_terms(self, text: str, complexity_level: ComplexityLevel) -> str:
        """Replace technical terms with family-friendly alternatives"""
        replacements = self.technical_terms.get(complexity_level.value, {})
        
        # Sort by length (longest first) to handle compound terms properly
        sorted_terms = sorted(replacements.items(), key=lambda x: len(x[0]), reverse=True)
        
        for technical_term, friendly_term in sorted_terms:
            # Case-insensitive replacement with word boundaries
            pattern = re.compile(r'\b' + re.escape(technical_term) + r'\b', re.IGNORECASE)
            text = pattern.sub(friendly_term, text)
        
        return text
    
    def _add_analogies(self, text: str, target_age_group: Optional[str]) -> str:
        """Add analogies to explain complex concepts"""
        if not target_age_group:
            target_age_group = "adult"
        
        analogies = self.analogies.get(target_age_group, {})
        
        for concept, analogy in analogies.items():
            # Check if the concept appears in the text (case-insensitive)
            if re.search(r'\b' + re.escape(concept) + r'\b', text, re.IGNORECASE):
                # Add analogy after the concept is mentioned
                pattern = re.compile(r'\b(' + re.escape(concept) + r')\b', re.IGNORECASE)
                replacement = f'\\1 (think of it like {analogy})'
                text = pattern.sub(replacement, text, count=1)
        
        return text
    
    def _adjust_complexity(self, text: str, complexity_level: ComplexityLevel) -> str:
        """Adjust response complexity based on target level"""
        modifiers = self.complexity_modifiers.get(complexity_level.value, {})
        
        if complexity_level == ComplexityLevel.SIMPLE:
            # Simplify sentence structure
            text = self._simplify_sentences(text)
            # Remove overly technical details
            text = self._remove_technical_details(text)
        elif complexity_level == ComplexityLevel.DETAILED:
            # Add more explanatory context
            text = self._add_explanatory_context(text)
        
        return text
    
    def _control_length(self, text: str, response_length: ResponseLength) -> str:
        """Control the length of the response"""
        sentences = text.split('. ')
        
        if response_length == ResponseLength.SHORT:
            # Keep only the most important sentences (first 2-3)
            sentences = sentences[:3]
        elif response_length == ResponseLength.LONG:
            # Keep all sentences and potentially add more detail
            pass  # Keep as is for now
        # MEDIUM is the default, no changes needed
        
        return '. '.join(sentences)
    
    def _add_encouraging_tone(self, text: str) -> str:
        """Add encouraging, supportive tone to the response"""
        # Add positive reinforcement phrases
        encouraging_starters = [
            "Great question! ",
            "You're smart to ask about this. ",
            "This is important for keeping your family safe. "
        ]
        
        encouraging_endings = [
            " Remember, taking these steps shows you care about your family's safety!",
            " You're doing the right thing by learning about this.",
            " Every small step helps keep your family more secure."
        ]
        
        # Randomly add encouraging elements (for now, just add to beginning)
        if not any(starter.strip() in text for starter in encouraging_starters):
            text = encouraging_starters[0] + text
        
        return text
    
    def _simplify_sentences(self, text: str) -> str:
        """Simplify complex sentence structures"""
        # Split long sentences at conjunctions
        text = re.sub(r',\s*(however|moreover|furthermore|additionally)', r'. \\1', text)
        
        # Replace complex phrases with simpler ones
        simplifications = {
            'in order to': 'to',
            'due to the fact that': 'because',
            'it is important to note that': '',
            'furthermore': 'also',
            'however': 'but',
            'therefore': 'so',
            'consequently': 'so'
        }
        
        for complex_phrase, simple_phrase in simplifications.items():
            text = re.sub(complex_phrase, simple_phrase, text, flags=re.IGNORECASE)
        
        return text
    
    def _remove_technical_details(self, text: str) -> str:
        """Remove overly technical details for simple responses"""
        # Remove content in parentheses that might be too technical
        text = re.sub(r'\([^)]*protocol[^)]*\)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\([^)]*algorithm[^)]*\)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\([^)]*encryption[^)]*\)', '', text, flags=re.IGNORECASE)
        
        return text
    
    def _add_explanatory_context(self, text: str) -> str:
        """Add more explanatory context for detailed responses"""
        # This could be expanded to add more context based on detected topics
        return text
    
    def _initialize_technical_terms(self) -> Dict[str, Dict[str, str]]:
        """Initialize technical term replacements by complexity level"""
        return {
            "simple": {
                "two-factor authentication": "double security check",
                "Wi-Fi": "wireless internet",
                "firewall": "security barrier",
                "malware": "bad software",
                "phishing": "fake messages trying to trick you",
                "encryption": "secret code protection",
                "authentication": "proving who you are",
                "vulnerability": "security weakness",
                "patch": "security fix",
                "antivirus": "protection software",
                "router": "internet box",
                "password": "secret word",
                "VPN": "private internet tunnel",
                "backup": "safety copy",
                "update": "improvement",
                "browser": "internet program",
                "download": "get from internet",
                "upload": "send to internet",
                "spam": "junk messages",
                "cookies": "website memory files"
            },
            "moderate": {
                "two-factor authentication": "two-step security verification",
                "firewall": "digital security barrier",
                "malware": "malicious software",
                "phishing": "deceptive messages designed to steal information",
                "encryption": "data protection through coding",
                "authentication": "identity verification process",
                "vulnerability": "security gap or weakness",
                "patch": "security update or fix",
                "router": "internet box",
                "VPN": "Virtual Private Network for secure connections",
                "spam": "unwanted or junk email messages",
                "cookies": "small files that websites store on your device"
            },
            "detailed": {
                # For detailed level, keep most technical terms but add brief explanations
                "firewall": "firewall (network security system)",
                "encryption": "encryption (data protection method)",
                "authentication": "authentication (identity verification)",
                "vulnerability": "vulnerability (security flaw)"
            }
        }
    
    def _initialize_analogies(self) -> Dict[str, Dict[str, str]]:
        """Initialize analogies by age group"""
        return {
            "child": {
                "firewall": "a security guard for your computer",
                "password": "a secret key to your digital house",
                "antivirus": "a doctor that keeps your computer healthy",
                "backup": "making a photocopy of your important drawings",
                "encryption": "writing in a secret code only you can read",
                "router": "the mailbox that delivers internet to your house",
                "phishing": "strangers trying to trick you with fake messages",
                "malware": "computer germs that make devices sick"
            },
            "teen": {
                "firewall": "a bouncer at a club checking who gets in",
                "VPN": "a private tunnel through the internet",
                "encryption": "putting your messages in a locked box",
                "two-factor authentication": "showing both your ID and a special code",
                "phishing": "fake messages pretending to be from real companies",
                "malware": "digital viruses that infect your devices"
            },
            "adult": {
                "firewall": "a security checkpoint for your network",
                "encryption": "converting information into a secret code",
                "VPN": "a secure, private pathway through the internet",
                "phishing": "fraudulent attempts to obtain sensitive information",
                "authentication": "proving your identity to access systems",
                "malware": "software designed to damage or gain unauthorized access"
            }
        }
    
    def _initialize_complexity_modifiers(self) -> Dict[str, Dict[str, str]]:
        """Initialize complexity level modifiers"""
        return {
            "simple": {
                "sentence_length": "short",
                "vocabulary": "basic",
                "examples": "everyday"
            },
            "moderate": {
                "sentence_length": "medium",
                "vocabulary": "mixed",
                "examples": "relatable"
            },
            "detailed": {
                "sentence_length": "varied",
                "vocabulary": "comprehensive",
                "examples": "technical"
            }
        }
    
    def generate_step_by_step_guide(self, 
                                   task_description: str,
                                   complexity_level: ComplexityLevel = ComplexityLevel.MODERATE) -> List[str]:
        """
        Generate step-by-step instructions for cybersecurity tasks
        
        Args:
            task_description: Description of the task to break down
            complexity_level: Target complexity level
            
        Returns:
            List[str]: List of step-by-step instructions
        """
        # This is a simplified implementation - in a real system, this would
        # use more sophisticated NLP to break down tasks
        
        steps = []
        
        # Basic step generation based on common cybersecurity tasks
        if "password" in task_description.lower():
            steps = self._generate_password_steps(complexity_level)
        elif "wifi" in task_description.lower() or "wi-fi" in task_description.lower():
            steps = self._generate_wifi_steps(complexity_level)
        elif "update" in task_description.lower():
            steps = self._generate_update_steps(complexity_level)
        else:
            # Generic steps
            steps = [
                "First, make sure you understand what needs to be done",
                "Gather any information or tools you might need",
                "Follow the recommended security practices",
                "Test that everything is working properly",
                "Keep a record of what you did for future reference"
            ]
        
        return steps
    
    def _generate_password_steps(self, complexity_level: ComplexityLevel) -> List[str]:
        """Generate password-related steps"""
        if complexity_level == ComplexityLevel.SIMPLE:
            return [
                "Think of a phrase you'll remember",
                "Make it at least 8 characters long",
                "Add some numbers and symbols",
                "Don't use the same password everywhere",
                "Write it down in a safe place"
            ]
        else:
            return [
                "Create a unique passphrase using unrelated words",
                "Ensure it's at least 12 characters long",
                "Include uppercase, lowercase, numbers, and symbols",
                "Use a different password for each important account",
                "Consider using a password manager to store them safely"
            ]
    
    def _generate_wifi_steps(self, complexity_level: ComplexityLevel) -> List[str]:
        """Generate Wi-Fi security steps"""
        if complexity_level == ComplexityLevel.SIMPLE:
            return [
                "Find your router (the internet box)",
                "Look for the settings button or website address",
                "Log in with the admin password (often on a sticker)",
                "Look for 'Security' or 'Wireless' settings",
                "Choose 'WPA2' or 'WPA3' protection",
                "Set a strong network password"
            ]
        else:
            return [
                "Access your router's admin interface via web browser",
                "Navigate to wireless security settings",
                "Select WPA3 (or WPA2 if WPA3 isn't available)",
                "Configure a strong network password",
                "Disable WPS if enabled",
                "Consider hiding your network name (SSID) for additional security",
                "Update the router's firmware if needed"
            ]
    
    def _generate_update_steps(self, complexity_level: ComplexityLevel) -> List[str]:
        """Generate software update steps"""
        if complexity_level == ComplexityLevel.SIMPLE:
            return [
                "Check if updates are available",
                "Make sure you're connected to Wi-Fi",
                "Start the update process",
                "Wait for it to finish (don't turn off your device)",
                "Restart your device if asked"
            ]
        else:
            return [
                "Check for available system and application updates",
                "Ensure stable internet connection and adequate battery/power",
                "Review update details and security patches included",
                "Initiate the update process during a convenient time",
                "Allow the system to restart and complete the installation",
                "Verify that all applications are working properly after update"
            ]


# Factory function for easy instantiation
def create_family_response_formatter() -> FamilyResponseFormatter:
    """Create a configured FamilyResponseFormatter instance"""
    return FamilyResponseFormatter()


# Example usage
if __name__ == "__main__":
    formatter = create_family_response_formatter()
    
    technical_response = "You should implement two-factor authentication on your router to prevent unauthorized access through brute force attacks on your WPA2 encryption."
    
    # Format for different audiences
    simple_response = formatter.format_response(
        technical_response,
        complexity_level=ComplexityLevel.SIMPLE,
        target_age_group="child"
    )
    
    moderate_response = formatter.format_response(
        technical_response,
        complexity_level=ComplexityLevel.MODERATE,
        target_age_group="adult"
    )
    
    print("Simple response:", simple_response)
    print("\nModerate response:", moderate_response)
    
    # Generate step-by-step guide
    steps = formatter.generate_step_by_step_guide("secure my wifi password")
    print("\nStep-by-step guide:")
    for i, step in enumerate(steps, 1):
        print(f"{i}. {step}")