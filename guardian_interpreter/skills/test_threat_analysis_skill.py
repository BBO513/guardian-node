"""
Unit tests for Threat Analysis Skill
Tests the threat analysis functionality for family cybersecurity guidance.
"""

import unittest
import sys
import os

# Add the skills directory to the path
sys.path.append(os.path.dirname(__file__))

from threat_analysis_skill import (
    ThreatDatabase, 
    ThreatPrioritizer, 
    FamilyThreatExplainer, 
    ThreatAnalysisSkill,
    run
)

class TestThreatDatabase(unittest.TestCase):
    """Test the ThreatDatabase class"""
    
    def setUp(self):
        self.db = ThreatDatabase()
    
    def test_get_threat_exists(self):
        """Test getting an existing threat"""
        threat = self.db.get_threat('phishing')
        self.assertIsNotNone(threat)
        self.assertEqual(threat['name'], 'Phishing Attacks')
        self.assertIn('description', threat)
        self.assertIn('prevention', threat)
    
    def test_get_threat_not_exists(self):
        """Test getting a non-existent threat"""
        threat = self.db.get_threat('nonexistent')
        self.assertIsNone(threat)
    
    def test_get_all_threats(self):
        """Test getting all threats"""
        threats = self.db.get_all_threats()
        self.assertIsInstance(threats, dict)
        self.assertGreater(len(threats), 0)
        self.assertIn('phishing', threats)
        self.assertIn('malware', threats)
    
    def test_search_threats(self):
        """Test searching for threats"""
        # Search for phishing
        results = self.db.search_threats('phishing')
        self.assertGreater(len(results), 0)
        
        # Search for email (should find phishing)
        results = self.db.search_threats('email')
        self.assertGreater(len(results), 0)
        
        # Search for something that doesn't exist
        results = self.db.search_threats('xyznothinghere')
        self.assertEqual(len(results), 0)

class TestThreatPrioritizer(unittest.TestCase):
    """Test the ThreatPrioritizer class"""
    
    def test_calculate_priority_score(self):
        """Test priority score calculation"""
        # High impact, high likelihood
        threat1 = {'family_impact': 'high', 'likelihood': 'high'}
        score1 = ThreatPrioritizer.calculate_priority_score(threat1)
        self.assertEqual(score1, 9)  # 3 * 3
        
        # Very high impact, very high likelihood
        threat2 = {'family_impact': 'very_high', 'likelihood': 'very_high'}
        score2 = ThreatPrioritizer.calculate_priority_score(threat2)
        self.assertEqual(score2, 16)  # 4 * 4
        
        # Low impact, low likelihood
        threat3 = {'family_impact': 'low', 'likelihood': 'low'}
        score3 = ThreatPrioritizer.calculate_priority_score(threat3)
        self.assertEqual(score3, 1)  # 1 * 1
    
    def test_prioritize_threats(self):
        """Test threat prioritization"""
        threats = [
            ('low_threat', {'family_impact': 'low', 'likelihood': 'low'}),
            ('high_threat', {'family_impact': 'very_high', 'likelihood': 'very_high'}),
            ('medium_threat', {'family_impact': 'medium', 'likelihood': 'medium'})
        ]
        
        prioritized = ThreatPrioritizer.prioritize_threats(threats)
        
        # Should be sorted by score (highest first)
        self.assertEqual(len(prioritized), 3)
        self.assertEqual(prioritized[0][0], 'high_threat')  # Highest score first
        self.assertEqual(prioritized[-1][0], 'low_threat')  # Lowest score last
        
        # Check scores are in descending order
        scores = [item[2] for item in prioritized]
        self.assertEqual(scores, sorted(scores, reverse=True))

class TestFamilyThreatExplainer(unittest.TestCase):
    """Test the FamilyThreatExplainer class"""
    
    def setUp(self):
        self.explainer = FamilyThreatExplainer()
        self.sample_threat = {
            'name': 'Test Threat',
            'description': 'A test threat for testing',
            'family_analogy': 'Like a test analogy',
            'examples': ['Example 1', 'Example 2'],
            'prevention': ['Prevention tip 1', 'Prevention tip 2'],
            'family_impact': 'high',
            'likelihood': 'medium'
        }
    
    def test_format_threat_explanation(self):
        """Test formatting a threat explanation"""
        explanation = self.explainer.format_threat_explanation('test', self.sample_threat)
        
        self.assertIn('Test Threat', explanation)
        self.assertIn('A test threat for testing', explanation)
        self.assertIn('Like a test analogy', explanation)
        self.assertIn('Example 1', explanation)
        self.assertIn('Prevention tip 1', explanation)
        self.assertIn('Impact: High', explanation)
    
    def test_format_threat_explanation_no_examples(self):
        """Test formatting without examples"""
        explanation = self.explainer.format_threat_explanation('test', self.sample_threat, include_examples=False)
        
        self.assertIn('Test Threat', explanation)
        self.assertNotIn('Example 1', explanation)
    
    def test_format_threat_summary(self):
        """Test formatting a threat summary"""
        threats = [
            ('threat1', {'name': 'Threat 1', 'description': 'First threat'}, 10),
            ('threat2', {'name': 'Threat 2', 'description': 'Second threat'}, 8)
        ]
        
        summary = self.explainer.format_threat_summary(threats)
        
        self.assertIn('Threat 1', summary)
        self.assertIn('Threat 2', summary)
        self.assertIn('First threat', summary)
        self.assertIn('Second threat', summary)
    
    def test_format_empty_threat_summary(self):
        """Test formatting an empty threat summary"""
        summary = self.explainer.format_threat_summary([])
        self.assertIn('No specific threats found', summary)

class TestThreatAnalysisSkill(unittest.TestCase):
    """Test the main ThreatAnalysisSkill class"""
    
    def setUp(self):
        self.skill = ThreatAnalysisSkill()
    
    def test_analyze_general_threats(self):
        """Test general threat analysis"""
        result = self.skill.analyze_general_threats()
        self.assertIsInstance(result, str)
        self.assertIn('Cybersecurity Threats', result)
        self.assertGreater(len(result), 100)  # Should be a substantial response
    
    def test_analyze_specific_threat_exact_match(self):
        """Test analyzing a specific threat with exact match"""
        result = self.skill.analyze_specific_threat('phishing')
        self.assertIsInstance(result, str)
        self.assertIn('Phishing', result)
        self.assertIn('protect', result.lower())
    
    def test_analyze_specific_threat_search(self):
        """Test analyzing a specific threat with search"""
        result = self.skill.analyze_specific_threat('email scam')
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 50)  # Should find something
    
    def test_analyze_specific_threat_not_found(self):
        """Test analyzing a non-existent threat"""
        result = self.skill.analyze_specific_threat('nonexistentthreat12345')
        self.assertIsInstance(result, str)
        self.assertIn("couldn't find", result)
    
    def test_get_current_threat_landscape(self):
        """Test getting current threat landscape"""
        result = self.skill.get_current_threat_landscape()
        self.assertIsInstance(result, str)
        self.assertIn('Current Cybersecurity Landscape', result)
        self.assertIn('Top 3 Threats', result)

class TestRunFunction(unittest.TestCase):
    """Test the main run function"""
    
    def test_run_no_args(self):
        """Test run function with no arguments"""
        result = run()
        self.assertIsInstance(result, str)
        self.assertIn('Current Cybersecurity Landscape', result)
    
    def test_run_current_threats(self):
        """Test run function asking for current threats"""
        result = run('current', 'threats')
        self.assertIsInstance(result, str)
        self.assertIn('Current Cybersecurity Landscape', result)
    
    def test_run_general_overview(self):
        """Test run function asking for general overview"""
        result = run('general', 'overview')
        self.assertIsInstance(result, str)
        self.assertIn('Cybersecurity Threats', result)
    
    def test_run_specific_threat(self):
        """Test run function with specific threat query"""
        result = run('phishing')
        self.assertIsInstance(result, str)
        self.assertIn('Phishing', result)
    
    def test_run_error_handling(self):
        """Test run function error handling"""
        # This should not raise an exception
        result = run('some', 'query', 'that', 'might', 'cause', 'issues')
        self.assertIsInstance(result, str)

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)