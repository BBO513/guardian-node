"""
Unit tests for Family Response Formatter module
Tests family-friendly response formatting and technical term replacement
"""

import unittest
from family_response_formatter import (
    FamilyResponseFormatter, ComplexityLevel, ResponseLength,
    create_family_response_formatter
)


class TestFamilyResponseFormatter(unittest.TestCase):
    """Test cases for FamilyResponseFormatter"""
    
    def setUp(self):
        self.formatter = create_family_response_formatter()
    
    def test_basic_response_formatting(self):
        """Test basic response formatting functionality"""
        technical_response = "Configure your firewall to block malware attacks."
        
        formatted = self.formatter.format_response(technical_response)
        
        # Should contain family-friendly terms
        self.assertIn("security barrier", formatted.lower())
        self.assertIn("malicious software", formatted.lower())
        # Should have encouraging tone
        self.assertIn("Great question!", formatted)
    
    def test_complexity_level_simple(self):
        """Test simple complexity level formatting"""
        technical_response = "Enable two-factor authentication on your router to prevent phishing attacks."
        
        simple_response = self.formatter.format_response(
            technical_response,
            complexity_level=ComplexityLevel.SIMPLE,
            target_age_group="child"
        )
        
        # Should use simple terms
        self.assertIn("double security check", simple_response)
        self.assertIn("internet box", simple_response)
        self.assertIn("fake messages", simple_response)
    
    def test_complexity_level_moderate(self):
        """Test moderate complexity level formatting"""
        technical_response = "Update your antivirus software to protect against malware."
        
        moderate_response = self.formatter.format_response(
            technical_response,
            complexity_level=ComplexityLevel.MODERATE
        )
        
        # Should use moderate technical terms
        self.assertIn("malicious software", moderate_response)
        # Should not be overly simplified
        self.assertNotIn("bad software", moderate_response)
    
    def test_complexity_level_detailed(self):
        """Test detailed complexity level formatting"""
        technical_response = "Configure firewall rules to block unauthorized access."
        
        detailed_response = self.formatter.format_response(
            technical_response,
            complexity_level=ComplexityLevel.DETAILED
        )
        
        # Should keep technical terms with explanations
        self.assertIn("firewall", detailed_response)
        # Should add explanatory context
        self.assertTrue(len(detailed_response) >= len(technical_response))
    
    def test_analogy_addition_child(self):
        """Test analogy addition for child audience"""
        technical_response = "A firewall protects your network."
        
        child_response = self.formatter.format_response(
            technical_response,
            target_age_group="child"
        )
        
        # Should include child-appropriate analogy
        self.assertIn("security guard", child_response)
    
    def test_analogy_addition_teen(self):
        """Test analogy addition for teen audience"""
        technical_response = "Use a VPN for secure browsing."
        
        teen_response = self.formatter.format_response(
            technical_response,
            target_age_group="teen"
        )
        
        # Should include teen-appropriate analogy
        self.assertIn("private tunnel", teen_response)
    
    def test_response_length_control_short(self):
        """Test short response length control"""
        long_technical_response = (
            "Firewalls are essential security tools. They monitor network traffic. "
            "They block unauthorized access. They prevent malware infections. "
            "Regular updates are important. Configuration should be reviewed periodically."
        )
        
        short_response = self.formatter.format_response(
            long_technical_response,
            response_length=ResponseLength.SHORT
        )
        
        # Should be shorter than original
        self.assertLess(len(short_response), len(long_technical_response))
        # Should contain key information
        self.assertIn("security", short_response.lower())
    
    def test_response_length_control_medium(self):
        """Test medium response length control"""
        technical_response = "Configure your router security settings properly."
        
        medium_response = self.formatter.format_response(
            technical_response,
            response_length=ResponseLength.MEDIUM
        )
        
        # Should maintain reasonable length
        self.assertGreater(len(medium_response), 0)
        self.assertIn("internet box", medium_response)
    
    def test_encouraging_tone_addition(self):
        """Test that encouraging tone is added to responses"""
        technical_response = "Update your software regularly."
        
        formatted = self.formatter.format_response(technical_response)
        
        # Should have encouraging elements
        encouraging_phrases = [
            "Great question!",
            "You're smart to ask",
            "important for keeping your family safe"
        ]
        
        has_encouraging_tone = any(phrase in formatted for phrase in encouraging_phrases)
        self.assertTrue(has_encouraging_tone)
    
    def test_technical_term_replacement(self):
        """Test comprehensive technical term replacement"""
        technical_response = (
            "Enable encryption and authentication on your Wi-Fi router. "
            "Install antivirus software and keep it updated. "
            "Be careful of phishing emails and malware downloads."
        )
        
        simple_response = self.formatter.format_response(
            technical_response,
            complexity_level=ComplexityLevel.SIMPLE
        )
        
        # Check that technical terms are replaced
        self.assertIn("secret code protection", simple_response)
        self.assertIn("proving who you are", simple_response)
        self.assertIn("wireless internet", simple_response)
        self.assertIn("protection software", simple_response)
        self.assertIn("fake messages", simple_response)
        self.assertIn("bad software", simple_response)
    
    def test_step_by_step_guide_generation(self):
        """Test step-by-step guide generation"""
        task_description = "create a strong password"
        
        steps = self.formatter.generate_step_by_step_guide(task_description)
        
        # Should return a list of steps
        self.assertIsInstance(steps, list)
        self.assertGreater(len(steps), 0)
        
        # Steps should be strings
        for step in steps:
            self.assertIsInstance(step, str)
            self.assertGreater(len(step), 0)
    
    def test_password_steps_simple(self):
        """Test password-related step generation for simple level"""
        steps = self.formatter.generate_step_by_step_guide(
            "create a password",
            complexity_level=ComplexityLevel.SIMPLE
        )
        
        # Should contain basic password advice
        step_text = " ".join(steps).lower()
        self.assertIn("8 characters", step_text)
        self.assertIn("numbers", step_text)
        self.assertIn("symbols", step_text)
    
    def test_wifi_steps_generation(self):
        """Test Wi-Fi security step generation"""
        steps = self.formatter.generate_step_by_step_guide("secure my wifi")
        
        # Should contain Wi-Fi specific steps
        step_text = " ".join(steps).lower()
        self.assertIn("router", step_text)
        self.assertIn("password", step_text)
        self.assertIn("wpa", step_text)
    
    def test_update_steps_generation(self):
        """Test software update step generation"""
        steps = self.formatter.generate_step_by_step_guide("update my software")
        
        # Should contain update-specific steps
        step_text = " ".join(steps).lower()
        self.assertIn("update", step_text)
        self.assertIn("restart", step_text)
    
    def test_sentence_simplification(self):
        """Test sentence structure simplification"""
        complex_response = (
            "Furthermore, it is important to note that you should update your software, "
            "however, you must ensure that you have a backup in order to prevent data loss."
        )
        
        simple_response = self.formatter.format_response(
            complex_response,
            complexity_level=ComplexityLevel.SIMPLE
        )
        
        # Should simplify complex phrases
        self.assertNotIn("Furthermore", simple_response)
        self.assertNotIn("it is important to note that", simple_response)
        self.assertNotIn("in order to", simple_response)
        # Should contain simplified versions
        self.assertIn("also", simple_response.lower())
        self.assertIn("to prevent", simple_response)


class TestFactoryFunction(unittest.TestCase):
    """Test factory function"""
    
    def test_create_family_response_formatter(self):
        """Test family response formatter factory"""
        formatter = create_family_response_formatter()
        self.assertIsInstance(formatter, FamilyResponseFormatter)
        
        # Should be able to format responses
        response = formatter.format_response("Test technical response")
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)


if __name__ == '__main__':
    unittest.main()