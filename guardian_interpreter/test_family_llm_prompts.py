"""
Unit tests for Family LLM Prompts module
Tests family-friendly system prompts and child safety filtering
"""

import unittest
from family_llm_prompts import (
    FamilyPromptManager, ChildSafetyFilter, FamilyContext, 
    ChildSafetyLevel, create_family_prompt_manager, create_child_safety_filter
)


class TestFamilyPromptManager(unittest.TestCase):
    """Test cases for FamilyPromptManager"""
    
    def setUp(self):
        self.prompt_manager = create_family_prompt_manager()
    
    def test_basic_system_prompt_generation(self):
        """Test basic system prompt generation"""
        prompt = self.prompt_manager.get_system_prompt()
        
        # Should contain key family assistant elements
        self.assertIn("Nodie", prompt)
        self.assertIn("Guardian Family Cybersecurity Assistant", prompt)
        self.assertIn("family-friendly language", prompt)
        self.assertIn("offline", prompt)
    
    def test_context_specific_prompts(self):
        """Test context-specific prompt modifications"""
        # Test child education context
        child_prompt = self.prompt_manager.get_system_prompt(
            context=FamilyContext.CHILD_EDUCATION
        )
        self.assertIn("age-appropriate explanations", child_prompt)
        self.assertIn("conversation starters", child_prompt)
        
        # Test parent guidance context
        parent_prompt = self.prompt_manager.get_system_prompt(
            context=FamilyContext.PARENT_GUIDANCE
        )
        self.assertIn("managing family digital safety", parent_prompt)
        self.assertIn("different age groups", parent_prompt)
        
        # Test device security context
        device_prompt = self.prompt_manager.get_system_prompt(
            context=FamilyContext.DEVICE_SECURITY
        )
        self.assertIn("step-by-step instructions", device_prompt)
        self.assertIn("securing family devices", device_prompt)
    
    def test_child_safe_mode_prompts(self):
        """Test child safety mode prompt modifications"""
        # Test strict safety mode
        strict_prompt = self.prompt_manager.get_system_prompt(
            child_safe_mode=True,
            safety_level=ChildSafetyLevel.STRICT
        )
        self.assertIn("positive, encouraging language", strict_prompt)
        self.assertIn("young children", strict_prompt)
        
        # Test moderate safety mode
        moderate_prompt = self.prompt_manager.get_system_prompt(
            child_safe_mode=True,
            safety_level=ChildSafetyLevel.MODERATE
        )
        self.assertIn("gentle, age-appropriate warnings", moderate_prompt)
        self.assertIn("good decision-making", moderate_prompt)
    
    def test_family_profile_personalization(self):
        """Test family profile-based personalization"""
        family_profile = {
            'members': [
                {'age_group': 'child', 'tech_skill_level': 'beginner'},
                {'age_group': 'adult', 'tech_skill_level': 'intermediate'}
            ],
            'devices': [
                {'device_type': 'smartphone'},
                {'device_type': 'tablet'}
            ],
            'security_preferences': {
                'threat_tolerance': 'low'
            }
        }
        
        personalized_prompt = self.prompt_manager.get_system_prompt(
            family_profile=family_profile
        )
        
        self.assertIn("child with beginner tech skills", personalized_prompt)
        # Check that both device types are mentioned (order may vary)
        self.assertIn("smartphone", personalized_prompt)
        self.assertIn("tablet", personalized_prompt)
        self.assertIn("very cautious security measures", personalized_prompt)
    
    def test_prompt_formatting(self):
        """Test complete prompt formatting"""
        system_prompt = "Test system prompt"
        user_prompt = "How do I secure my WiFi?"
        
        formatted = self.prompt_manager.format_prompt_for_context(
            user_prompt, FamilyContext.DEVICE_SECURITY, system_prompt
        )
        
        self.assertIn("System: Test system prompt", formatted)
        self.assertIn("Device Security Help:", formatted)
        self.assertIn("Human: How do I secure my WiFi?", formatted)
        self.assertIn("Assistant:", formatted)


class TestChildSafetyFilter(unittest.TestCase):
    """Test cases for ChildSafetyFilter"""
    
    def setUp(self):
        self.safety_filter = create_child_safety_filter()
    
    def test_strict_filtering(self):
        """Test strict child safety filtering"""
        scary_response = "A hacker could steal your data and cause terrible damage to your computer."
        
        filtered = self.safety_filter.filter_response(
            scary_response, ChildSafetyLevel.STRICT
        )
        
        # Should replace scary terms
        self.assertNotIn("hacker", filtered.lower())
        self.assertNotIn("steal", filtered.lower())
        self.assertNotIn("terrible", filtered.lower())
        
        # Should contain child-friendly alternatives
        self.assertIn("person who breaks computer rules", filtered)
        self.assertIn("take without permission", filtered)
    
    def test_moderate_filtering(self):
        """Test moderate child safety filtering"""
        response = "Hackers might try to access your information, but good security prevents this."
        
        filtered = self.safety_filter.filter_response(
            response, ChildSafetyLevel.MODERATE
        )
        
        # Should replace some scary terms but keep educational content
        self.assertNotIn("Hackers", filtered)
        self.assertIn("person who", filtered)  # Check for replacement pattern
        self.assertIn("good security prevents", filtered)
    
    def test_standard_filtering(self):
        """Test standard family-friendly filtering"""
        response = "Cybercriminals use malware to exploit vulnerabilities in your system."
        
        filtered = self.safety_filter.filter_response(
            response, ChildSafetyLevel.STANDARD
        )
        
        # Should keep most technical terms but remove inappropriate language
        self.assertIn("malware", filtered)
        self.assertIn("vulnerabilities", filtered)
        # Should not contain profanity (if any was present)
    
    def test_no_false_positives(self):
        """Test that normal family-friendly content isn't over-filtered"""
        good_response = "To keep your family safe online, use strong passwords and keep software updated."
        
        # Should remain unchanged at all safety levels
        strict_filtered = self.safety_filter.filter_response(
            good_response, ChildSafetyLevel.STRICT
        )
        moderate_filtered = self.safety_filter.filter_response(
            good_response, ChildSafetyLevel.MODERATE
        )
        standard_filtered = self.safety_filter.filter_response(
            good_response, ChildSafetyLevel.STANDARD
        )
        
        self.assertEqual(good_response, strict_filtered)
        self.assertEqual(good_response, moderate_filtered)
        self.assertEqual(good_response, standard_filtered)


class TestFactoryFunctions(unittest.TestCase):
    """Test factory functions"""
    
    def test_create_family_prompt_manager(self):
        """Test family prompt manager factory"""
        manager = create_family_prompt_manager()
        self.assertIsInstance(manager, FamilyPromptManager)
        
        # Should be able to generate prompts
        prompt = manager.get_system_prompt()
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 0)
    
    def test_create_child_safety_filter(self):
        """Test child safety filter factory"""
        filter_obj = create_child_safety_filter()
        self.assertIsInstance(filter_obj, ChildSafetyFilter)
        
        # Should be able to filter responses
        filtered = filter_obj.filter_response("Test response", ChildSafetyLevel.STANDARD)
        self.assertIsInstance(filtered, str)


if __name__ == '__main__':
    unittest.main()