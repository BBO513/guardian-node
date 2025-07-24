"""
Unit tests for Child Education Skill
Tests the child cybersecurity education functionality.
"""

import unittest
import sys
import os

# Add the skills directory to the path
sys.path.append(os.path.dirname(__file__))

from child_education_skill import (
    ChildEducationDatabase,
    ChildEducationFormatter,
    ChildEducationSkill,
    run
)

class TestChildEducationDatabase(unittest.TestCase):
    """Test the ChildEducationDatabase class"""
    
    def setUp(self):
        self.db = ChildEducationDatabase()
    
    def test_age_groups_structure(self):
        """Test that all age groups have required structure"""
        required_keys = ['age_range', 'key_concepts', 'activities', 'conversation_starters']
        
        for age_group, content in self.db.age_groups.items():
            for key in required_keys:
                self.assertIn(key, content, f"Missing {key} in {age_group}")
            
            # Check activities structure
            for activity in content['activities']:
                activity_keys = ['name', 'description', 'materials', 'duration', 'instructions']
                for key in activity_keys:
                    self.assertIn(key, activity, f"Missing {key} in activity")
                self.assertIsInstance(activity['instructions'], list)
                self.assertGreater(len(activity['instructions']), 0)
    
    def test_safety_scenarios_structure(self):
        """Test that all safety scenarios have required structure"""
        for scenario_id, scenario_data in self.db.safety_scenarios.items():
            self.assertIn('scenario', scenario_data)
            self.assertIn('age_responses', scenario_data)
            
            # Check that all age groups have responses
            expected_ages = ['preschool', 'elementary', 'middle_school', 'high_school']
            for age in expected_ages:
                self.assertIn(age, scenario_data['age_responses'])
    
    def test_age_groups_exist(self):
        """Test that expected age groups exist"""
        expected_ages = ['preschool', 'elementary', 'middle_school', 'high_school']
        for age in expected_ages:
            self.assertIn(age, self.db.age_groups)
    
    def test_content_quality(self):
        """Test that content is substantial and appropriate"""
        for age_group, content in self.db.age_groups.items():
            # Should have multiple key concepts
            self.assertGreaterEqual(len(content['key_concepts']), 3)
            
            # Should have multiple activities
            self.assertGreaterEqual(len(content['activities']), 2)
            
            # Should have conversation starters
            self.assertGreaterEqual(len(content['conversation_starters']), 3)

class TestChildEducationFormatter(unittest.TestCase):
    """Test the ChildEducationFormatter class"""
    
    def setUp(self):
        self.formatter = ChildEducationFormatter()
        self.sample_content = {
            'age_range': '6-10 years',
            'key_concepts': ['Test concept 1', 'Test concept 2'],
            'activities': [
                {
                    'name': 'Test Activity',
                    'description': 'A test activity',
                    'materials': 'Test materials',
                    'duration': '10 minutes',
                    'instructions': ['Step 1', 'Step 2']
                }
            ],
            'conversation_starters': ['Test question 1?', 'Test question 2?']
        }
        
        self.sample_scenario = {
            'scenario': 'Test scenario description',
            'age_responses': {
                'preschool': 'Preschool response',
                'elementary': 'Elementary response'
            }
        }
    
    def test_format_age_appropriate_guide(self):
        """Test formatting age-appropriate guide"""
        guide = self.formatter.format_age_appropriate_guide('elementary', self.sample_content)
        
        self.assertIn('6-10 years', guide)
        self.assertIn('Key Concepts', guide)
        self.assertIn('Test concept 1', guide)
        self.assertIn('Fun Learning Activities', guide)
        self.assertIn('Test Activity', guide)
        self.assertIn('Conversation Starters', guide)
        self.assertIn('Test question 1', guide)
    
    def test_format_scenario_guidance(self):
        """Test formatting scenario guidance"""
        guidance = self.formatter.format_scenario_guidance('test_scenario', self.sample_scenario)
        
        self.assertIn('Safety Scenario', guidance)
        self.assertIn('Test scenario description', guidance)
        self.assertIn('Age-Appropriate Responses', guidance)
        self.assertIn('Preschool response', guidance)
        self.assertIn('Elementary response', guidance)
    
    def test_format_activity_instructions(self):
        """Test formatting activity instructions"""
        activity = self.sample_content['activities'][0]
        instructions = self.formatter.format_activity_instructions(activity)
        
        self.assertIn('Test Activity', instructions)
        self.assertIn('A test activity', instructions)
        self.assertIn('10 minutes', instructions)
        self.assertIn('Test materials', instructions)
        self.assertIn('Step 1', instructions)
        self.assertIn('Step 2', instructions)

class TestChildEducationSkill(unittest.TestCase):
    """Test the main ChildEducationSkill class"""
    
    def setUp(self):
        self.skill = ChildEducationSkill()
    
    def test_get_age_appropriate_content_valid(self):
        """Test getting content for valid age group"""
        content = self.skill.get_age_appropriate_content('elementary')
        
        self.assertIsInstance(content, str)
        self.assertIn('6-10 years', content)
        self.assertIn('Key Concepts', content)
        self.assertIn('Fun Learning Activities', content)
        self.assertIn('Conversation Starters', content)
    
    def test_get_age_appropriate_content_invalid(self):
        """Test getting content for invalid age group"""
        content = self.skill.get_age_appropriate_content('invalid_age')
        
        self.assertIsInstance(content, str)
        self.assertIn('age groups', content)
    
    def test_get_safety_scenario_guidance_specific(self):
        """Test getting guidance for specific scenario"""
        guidance = self.skill.get_safety_scenario_guidance('stranger')
        
        self.assertIsInstance(guidance, str)
        self.assertIn('Safety Scenario', guidance)
        self.assertIn('stranger', guidance.lower())
    
    def test_get_safety_scenario_guidance_all(self):
        """Test getting all safety scenarios"""
        guidance = self.skill.get_safety_scenario_guidance()
        
        self.assertIsInstance(guidance, str)
        self.assertIn('Common Safety Scenarios', guidance)
    
    def test_get_activity_instructions(self):
        """Test getting activity instructions"""
        instructions = self.skill.get_activity_instructions('password', 'elementary')
        
        self.assertIsInstance(instructions, str)
        # Should either find the activity or provide helpful response
        self.assertGreater(len(instructions), 50)
    
    def test_get_conversation_starters_specific_age(self):
        """Test getting conversation starters for specific age"""
        starters = self.skill.get_conversation_starters('elementary')
        
        self.assertIsInstance(starters, str)
        self.assertIn('Conversation Starters', starters)
        self.assertIn('6-10 years', starters)
    
    def test_get_conversation_starters_all_ages(self):
        """Test getting conversation starters for all ages"""
        starters = self.skill.get_conversation_starters()
        
        self.assertIsInstance(starters, str)
        self.assertIn('Conversation Starters', starters)
        self.assertIn('Tips for Great Conversations', starters)
    
    def test_get_general_education_overview(self):
        """Test getting general education overview"""
        overview = self.skill.get_general_education_overview()
        
        self.assertIsInstance(overview, str)
        self.assertIn('Family Cybersecurity Education', overview)
        self.assertIn('3-5 years', overview)  # Preschool age range
        self.assertIn('14-18 years', overview)  # High school age range

class TestRunFunction(unittest.TestCase):
    """Test the main run function"""
    
    def test_run_no_args(self):
        """Test run function with no arguments"""
        result = run()
        self.assertIsInstance(result, str)
        self.assertIn('Family Cybersecurity Education', result)
    
    def test_run_age_specific(self):
        """Test run function with age-specific query"""
        result = run('elementary', 'kids')
        self.assertIsInstance(result, str)
        self.assertIn('6-10 years', result)
    
    def test_run_activity_query(self):
        """Test run function with activity query"""
        result = run('activities', 'for', 'elementary')
        self.assertIsInstance(result, str)
        self.assertIn('activities', result.lower())
    
    def test_run_conversation_query(self):
        """Test run function with conversation query"""
        result = run('conversation', 'starters')
        self.assertIsInstance(result, str)
        self.assertIn('Conversation Starters', result)
    
    def test_run_scenario_query(self):
        """Test run function with scenario query"""
        result = run('cyberbullying', 'scenario')
        self.assertIsInstance(result, str)
        self.assertIn('Safety Scenario', result)
    
    def test_run_stranger_query(self):
        """Test run function with stranger danger query"""
        result = run('stranger', 'danger')
        self.assertIsInstance(result, str)
        self.assertIn('stranger', result.lower())
    
    def test_run_bullying_query(self):
        """Test run function with bullying query"""
        result = run('cyberbullying')
        self.assertIsInstance(result, str)
        self.assertIn('mean', result.lower())
    
    def test_run_general_query(self):
        """Test run function with general query"""
        result = run('overview')
        self.assertIsInstance(result, str)
        self.assertIn('Family Cybersecurity Education', result)
    
    def test_run_error_handling(self):
        """Test run function error handling"""
        # This should not raise an exception
        result = run('some', 'complex', 'query', 'that', 'might', 'cause', 'issues')
        self.assertIsInstance(result, str)

class TestAgeGroupContent(unittest.TestCase):
    """Test content for each age group"""
    
    def setUp(self):
        self.skill = ChildEducationSkill()
    
    def test_preschool_content(self):
        """Test preschool content"""
        result = run('preschool')
        self.assertIn('3-5 years', result)
        self.assertIn('permission', result.lower())
    
    def test_elementary_content(self):
        """Test elementary content"""
        result = run('elementary')
        self.assertIn('6-10 years', result)
        self.assertIn('password', result.lower())
    
    def test_middle_school_content(self):
        """Test middle school content"""
        result = run('middle', 'school')
        self.assertIn('11-13 years', result)
        self.assertIn('social media', result.lower())
    
    def test_high_school_content(self):
        """Test high school content"""
        result = run('high', 'school')
        self.assertIn('14-18 years', result)
        self.assertIn('digital reputation', result.lower())

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)