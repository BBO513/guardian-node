"""
Family-Friendly LLM System Prompts for Guardian Node
Provides specialized system prompts and formatting for family cybersecurity assistance.
"""

from typing import Dict, Optional
from enum import Enum
import re


class FamilyContext(Enum):
    """Different family contexts for prompt customization"""
    GENERAL = "general"
    CHILD_EDUCATION = "child_education"
    PARENT_GUIDANCE = "parent_guidance"
    DEVICE_SECURITY = "device_security"
    THREAT_EXPLANATION = "threat_explanation"
    EMERGENCY_RESPONSE = "emergency_response"


class ChildSafetyLevel(Enum):
    """Child safety filtering levels"""
    STRICT = "strict"      # Very child-friendly, no scary content
    MODERATE = "moderate"  # Age-appropriate with gentle warnings
    STANDARD = "standard"  # Normal family-friendly content


class FamilyPromptManager:
    """
    Manages family-friendly system prompts and response formatting
    """
    
    def __init__(self):
        self.base_prompts = self._initialize_base_prompts()
        self.context_modifiers = self._initialize_context_modifiers()
        self.child_safety_filters = self._initialize_safety_filters()
    
    def _initialize_base_prompts(self) -> Dict[str, str]:
        return {
            "family_assistant": (
                "You are Nodie, the Guardian Family Cybersecurity Assistant. You are a friendly, knowledgeable AI that helps families stay safe online. You run completely offline on their Guardian Node device to protect their privacy.\n\n"
                "Your role is to:\n"
                "- Explain cybersecurity concepts in simple, family-friendly language\n"
                "- Provide practical security advice that families can actually follow\n"
                "- Use analogies and examples that relate to everyday family life\n"
                "- Be encouraging and supportive, never condescending or scary\n"
                "- Focus on actionable steps rather than technical details\n"
                "- Prioritize the most important security measures first\n\n"
                "Communication style:\n"
                "- Use warm, conversational language like talking to a neighbor\n"
                "- Avoid technical jargon unless necessary, and always explain terms simply\n"
                "- Break complex topics into easy-to-understand pieces\n"
                "- Use analogies from home security, car safety, or other familiar concepts\n"
                "- Be patient and thorough in explanations\n"
                "- Acknowledge when something might be challenging and offer simpler alternatives\n\n"
                "Remember: You're helping families protect what matters most to them - their safety, privacy, and peace of mind."
            )
        }
    
    def _initialize_context_modifiers(self) -> Dict[FamilyContext, str]:
        return {
            FamilyContext.CHILD_EDUCATION: (
                "CHILD EDUCATION FOCUS:\n"
                "- Create age-appropriate explanations that children can understand\n"
                "- Use fun analogies and examples from games, school, or activities kids enjoy\n"
                "- Focus on building good habits rather than fear\n"
                "- Provide conversation starters for parents to discuss with children\n"
                "- Make cybersecurity feel empowering, not scary\n"
                "- Include interactive elements or activities when possible"
            ),
            FamilyContext.PARENT_GUIDANCE: (
                "PARENT GUIDANCE FOCUS:\n"
                "- Provide practical advice for managing family digital safety\n"
                "- Include tips for different age groups and tech skill levels\n"
                "- Offer strategies for having cybersecurity conversations with children\n"
                "- Balance protection with age-appropriate independence\n"
                "- Address common parental concerns about online safety\n"
                "- Suggest family rules and agreements for digital device use"
            ),
            FamilyContext.DEVICE_SECURITY: (
                "DEVICE SECURITY FOCUS:\n"
                "- Provide step-by-step instructions for securing family devices\n"
                "- Consider different devices: phones, tablets, computers, smart home devices\n"
                "- Adjust recommendations based on user's technical skill level\n"
                "- Prioritize the most important security settings first\n"
                "- Explain why each security measure matters for family safety\n"
                "- Offer alternatives if recommended steps are too complex"
            ),
            FamilyContext.THREAT_EXPLANATION: (
                "THREAT EXPLANATION FOCUS:\n"
                "- Explain cybersecurity threats in non-scary, factual terms\n"
                "- Focus on prevention rather than detailed attack methods\n"
                "- Use analogies to physical world safety (locks, strangers, etc.)\n"
                "- Emphasize that most threats are preventable with good habits\n"
                "- Provide immediate action steps if a threat is detected\n"
                "- Reassure families while keeping them appropriately cautious"
            ),
            FamilyContext.EMERGENCY_RESPONSE: (
                "EMERGENCY RESPONSE FOCUS:\n"
                "- Provide clear, immediate action steps for security incidents\n"
                "- Stay calm and reassuring while being direct about necessary actions\n"
                "- Prioritize stopping ongoing threats and protecting family data\n"
                "- Offer both immediate and follow-up actions\n"
                "- Include when to seek additional help or contact authorities\n"
                "- Focus on recovery and prevention of future incidents"
            ),
        }
    
    def _initialize_safety_filters(self) -> Dict[ChildSafetyLevel, str]:
        return {
            ChildSafetyLevel.STRICT: (
                "CHILD SAFETY - STRICT MODE:\n"
                "- Use only positive, encouraging language suitable for young children\n"
                "- Replace scary terms with gentle, child-friendly alternatives\n"
                "- Focus on building good habits rather than discussing threats\n"
                "- Use analogies from familiar, safe activities (games, school, family)\n"
                "- Avoid any mention of specific attack methods or scary scenarios\n"
                "- Emphasize that adults are there to help and keep them safe\n"
                "- Make cybersecurity feel like a fun game or learning activity"
            ),
            ChildSafetyLevel.MODERATE: (
                "CHILD SAFETY - MODERATE MODE:\n"
                "- Use age-appropriate language with gentle, age-appropriate warnings\n"
                "- Explain why security matters without being frightening\n"
                "- Focus on good decision-making and smart choices online\n"
                "- Use analogies to everyday safety (crossing streets, talking to strangers)\n"
                "- Provide reassurance that following safety rules keeps them protected\n"
                "- Include parents/guardians in security discussions\n"
                "- Balance awareness with confidence-building"
            ),
            ChildSafetyLevel.STANDARD: (
                "CHILD SAFETY - STANDARD MODE:\n"
                "- Use family-friendly language appropriate for all ages\n"
                "- Explain security concepts clearly without unnecessary alarm\n"
                "- Focus on practical steps families can take together\n"
                "- Use positive reinforcement for good security practices\n"
                "- Avoid graphic descriptions of cyber attacks or their consequences\n"
                "- Emphasize prevention and preparedness over fear-based messaging"
            ),
        } 
   
    def _generate_personalization(self, family_profile: Optional[Dict]) -> str:
        if not family_profile:
            return ""
        
        personalization_parts = []
        
        # Add member-specific guidance
        if 'members' in family_profile:
            members = family_profile['members']
            child_members = [m for m in members if m.get('age_group') == 'child']
            adult_members = [m for m in members if m.get('age_group') == 'adult']
            
            if child_members:
                child_skills = [m.get('tech_skill_level', 'beginner') for m in child_members]
                if 'beginner' in child_skills:
                    personalization_parts.append(
                        "This family includes child with beginner tech skills - provide extra simple explanations and focus on basic safety habits."
                    )
            
            if adult_members:
                adult_skills = [m.get('tech_skill_level', 'intermediate') for m in adult_members]
                if 'advanced' in adult_skills:
                    personalization_parts.append(
                        "Some family members have advanced tech skills - you can include more detailed technical guidance when appropriate."
                    )
        
        # Add device-specific guidance
        if 'devices' in family_profile:
            device_types = [d.get('device_type', '') for d in family_profile['devices']]
            unique_devices = list(set(device_types))
            if unique_devices:
                device_list = ', '.join(unique_devices)
                personalization_parts.append(
                    f"This family uses these devices: {device_list}. Tailor security advice to these specific device types."
                )
        
        # Add security preference guidance
        if 'security_preferences' in family_profile:
            threat_tolerance = family_profile['security_preferences'].get('threat_tolerance', 'medium')
            if threat_tolerance == 'low':
                personalization_parts.append(
                    "This family prefers very cautious security measures - recommend comprehensive protection even if it requires more effort."
                )
            elif threat_tolerance == 'high':
                personalization_parts.append(
                    "This family is comfortable with moderate security risks - focus on essential protections that don't interfere with daily use."
                )
        
        return "\n".join(personalization_parts) if personalization_parts else ""
    
    def _get_context_prefix(self, context: FamilyContext) -> str:
        prefix_map = {
            FamilyContext.CHILD_EDUCATION: "Child Cybersecurity Education:",
            FamilyContext.EMERGENCY_RESPONSE: "SECURITY EMERGENCY - Immediate Help Needed:",
            FamilyContext.THREAT_EXPLANATION: "Threat Information Request:",
            FamilyContext.PARENT_GUIDANCE: "Parent Guidance Request:",
            FamilyContext.DEVICE_SECURITY: "Device Security Help:",
            FamilyContext.GENERAL: "Family Cybersecurity Question:"
        }
        return prefix_map.get(context, "Family Cybersecurity Question:")
    
    def get_system_prompt(self, 
                         context: FamilyContext = FamilyContext.GENERAL,
                         child_safe_mode: bool = False,
                         safety_level: ChildSafetyLevel = ChildSafetyLevel.STANDARD,
                         family_profile: Optional[Dict] = None) -> str:
        """
        Generate a family-friendly system prompt based on context and safety requirements
        """
        base_prompt = self.base_prompts["family_assistant"]
        
        if context in self.context_modifiers:
            base_prompt += "\n\n" + self.context_modifiers[context]
        
        if child_safe_mode:
            safety_instructions = self.child_safety_filters[safety_level]
            base_prompt += "\n\n" + safety_instructions
        
        if family_profile:
            personalization = self._generate_personalization(family_profile)
            if personalization:
                base_prompt += "\n\n" + personalization
        
        return base_prompt
    
    def format_prompt_for_context(self, 
                                user_prompt: str, 
                                context: FamilyContext,
                                system_prompt: str) -> str:
        """
        Format the complete prompt for LLM with proper structure
        """
        context_prefix = self._get_context_prefix(context)
        
        formatted_prompt = f"System: {system_prompt}\n\n{context_prefix}\nHuman: {user_prompt}\nAssistant:"
        
        return formatted_prompt


# Factory functions for easy instantiation
def create_family_prompt_manager() -> FamilyPromptManager:
    """Create a configured FamilyPromptManager instance"""
    return FamilyPromptManager()


# --------------- TEST EXAMPLE --------------- #
if __name__ == "__main__":
    fpm = FamilyPromptManager()
    
    family_profile = {
        "children": [{"age": 8}, {"age": 13}],
        "tech_level": "beginner"
    }
    
    sys_prompt = fpm.get_system_prompt(
        context=FamilyContext.CHILD_EDUCATION,
        child_safe_mode=True,
        safety_level=ChildSafetyLevel.STRICT,
        family_profile=family_profile
    )
    
    final_prompt = fpm.format_prompt_for_context(
        user_prompt="How do I check if my WiFi is safe?",
        context=FamilyContext.CHILD_EDUCATION,
        system_prompt=sys_prompt
    )
    
    print(final_prompt)


class ChildSafetyFilter:
    """
    Filters LLM responses to ensure child-appropriate content
    """
    
    def __init__(self):
        self.scary_terms = self._initialize_scary_terms()
        self.child_friendly_replacements = self._initialize_replacements()
    
    def filter_response(self, response: str, safety_level: ChildSafetyLevel) -> str:
        """
        Filter a response based on child safety level
        
        Args:
            response: The original LLM response
            safety_level: The level of filtering to apply
            
        Returns:
            str: Filtered response appropriate for the safety level
        """
        if safety_level == ChildSafetyLevel.STRICT:
            return self._apply_strict_filtering(response)
        elif safety_level == ChildSafetyLevel.MODERATE:
            return self._apply_moderate_filtering(response)
        else:  # STANDARD
            return self._apply_standard_filtering(response)
    
    def _apply_strict_filtering(self, response: str) -> str:
        """Apply strict child safety filtering"""
        filtered = response
        
        # Replace scary terms with child-friendly alternatives
        for scary_term, replacement in self.scary_terms['strict'].items():
            # Case-insensitive replacement
            pattern = re.compile(re.escape(scary_term), re.IGNORECASE)
            filtered = pattern.sub(replacement, filtered)
        
        return filtered
    
    def _apply_moderate_filtering(self, response: str) -> str:
        """Apply moderate child safety filtering"""
        filtered = response
        
        # Replace some scary terms with gentler alternatives
        for scary_term, replacement in self.scary_terms['moderate'].items():
            pattern = re.compile(re.escape(scary_term), re.IGNORECASE)
            filtered = pattern.sub(replacement, filtered)
        
        return filtered
    
    def _apply_standard_filtering(self, response: str) -> str:
        """Apply standard family-friendly filtering"""
        # For standard level, we keep most content as-is
        return response
    
    def _initialize_scary_terms(self) -> Dict[str, Dict[str, str]]:
        """Initialize scary terms and their child-friendly replacements"""
        return {
            'strict': {
                'hacker': 'person who breaks computer rules',
                'hackers': 'people who break computer rules',
                'steal': 'take without permission',
                'stolen': 'taken without permission',
                'terrible': 'concerning',
                'scary': 'concerning',
                'attack': 'try to cause problems',
                'attacks': 'try to cause problems',
                'malware': 'bad computer programs',
                'virus': 'computer program that causes problems',
                'dangerous': 'not safe'
            },
            'moderate': {
                'hacker': 'person who tries to access computers without permission',
                'hackers': 'people who try to access computers without permission',
                'terrible': 'very concerning',
                'devastating': 'very harmful'
            }
        }
    
    def _initialize_replacements(self) -> Dict[str, str]:
        """Initialize additional child-friendly replacements"""
        return {
            'identity theft': 'someone pretending to be you online',
            'financial fraud': 'someone using your money information incorrectly',
            'data breach': 'when private information gets seen by the wrong people'
        }


def create_child_safety_filter() -> ChildSafetyFilter:
    """Create a configured ChildSafetyFilter instance"""
    return ChildSafetyFilter()