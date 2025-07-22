"""
Family Skills Registry
Integrates family cybersecurity skills with Guardian Interpreter skill system
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

# Import family skills
from guardian_interpreter.skills import family_cyber_skills, threat_analysis_skill, device_guidance_skill, child_education_skill

class FamilySkillRegistry:
    """Registry for family cybersecurity skills"""
    
    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger(__name__)
        self.skills: Dict[str, Any] = {}
        self._initialize_skills()
    
    def _initialize_skills(self):
        """Initialize and register all family skills"""
        try:
            # Register family skills with descriptive names
            self.skills = {
                'family_cyber_skills': FamilyCyberSkills(),
                'threat_analysis_skill': ThreatAnalysisSkill(),
                'device_guidance_skill': DeviceGuidanceSkill(),
                'child_education_skill': ChildEducationSkill()
            }
            
            self.logger.info(f"Initialized {len(self.skills)} family skills")
            
        except Exception as e:
            self.logger.error(f"Error initializing family skills: {e}")
            self.skills = {}
    
    def get_skill(self, skill_name: str) -> Optional[Any]:
        """Get a skill by name"""
        return self.skills.get(skill_name)
    
    def list_skills(self) -> Dict[str, str]:
        """List all available family skills with descriptions"""
        skill_descriptions = {}
        
        for name, skill in self.skills.items():
            # Try to get description from skill docstring
            description = "Family cybersecurity skill"
            if hasattr(skill, '__doc__') and skill.__doc__:
                description = skill.__doc__.strip().split('\n')[0]
            elif hasattr(skill, 'get_description'):
                description = skill.get_description()
            
            skill_descriptions[name] = description
        
        return skill_descriptions
    
    def execute_skill(self, skill_name: str, *args, **kwargs) -> Any:
        """Execute a skill by name"""
        skill = self.get_skill(skill_name)
        if not skill:
            raise ValueError(f"Skill not found: {skill_name}")
        
        if hasattr(skill, 'run'):
            return skill.run(*args, **kwargs)
        else:
            raise AttributeError(f"Skill {skill_name} does not have a run method")

# Wrapper classes to make family skills compatible with Guardian skill system
class FamilyCyberSkills:
    """Main family cybersecurity skills coordinator"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def run(self, *args, **kwargs):
        """Main entry point for family cybersecurity skills"""
        return family_cyber_skills.run(*args, **kwargs)
    
    def get_description(self):
        return "Main family cybersecurity assistance and guidance"

class ThreatAnalysisSkill:
    """Family-friendly threat analysis skill"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def run(self, *args, **kwargs):
        """Analyze cybersecurity threats for families"""
        return threat_analysis_skill.run(*args, **kwargs)
    
    def get_description(self):
        return "Analyze and explain cybersecurity threats in family-friendly terms"

class DeviceGuidanceSkill:
    """Family device security guidance skill"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def run(self, *args, **kwargs):
        """Provide device security guidance for families"""
        return device_guidance_skill.run(*args, **kwargs)
    
    def get_description(self):
        return "Provide security guidance for family devices and technology"

class ChildEducationSkill:
    """Child cybersecurity education skill"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def run(self, *args, **kwargs):
        """Provide cybersecurity education for children"""
        return child_education_skill.run(*args, **kwargs)
    
    def get_description(self):
        return "Age-appropriate cybersecurity education and activities for children"

# Global registry instance
_family_skill_registry = None

def get_family_skill_registry(logger: logging.Logger = None) -> FamilySkillRegistry:
    """Get the global family skill registry instance"""
    global _family_skill_registry
    if _family_skill_registry is None:
        _family_skill_registry = FamilySkillRegistry(logger)
    return _family_skill_registry