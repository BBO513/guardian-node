#!/usr/bin/env python3
"""
Unit tests for the Family Cybersecurity Recommendation Engine
"""

import unittest
import logging
from datetime import datetime, timedelta
from unittest.mock import Mock

from recommendation_engine import (
    RecommendationEngine, SecurityRecommendation, FamilyProfile,
    Priority, Difficulty
)

class TestSecurityRecommendation(unittest.TestCase):
    """Test SecurityRecommendation data model"""
    
    def setUp(self):
        self.sample_recommendation = SecurityRecommendation(
            recommendation_id="test_rec_001",
            title="Test Recommendation",
            description="A test security recommendation",
            priority=Priority.HIGH,
            difficulty=Difficulty.MODERATE,
            estimated_time="30 minutes",
            steps=["Step 1", "Step 2", "Step 3"],
            applicable_devices=["device_001", "device_002"],
            family_members=["member_001"],
            category="authentication",
            created_at=datetime.now()
        )
    
    def test_recommendation_creation(self):
        """Test creating a SecurityRecommendation"""
        self.assertEqual(self.sample_recommendation.recommendation_id, "test_rec_001")
        self.assertEqual(self.sample_recommendation.priority, Priority.HIGH)
        self.assertEqual(self.sample_recommendation.difficulty, Difficulty.MODERATE)
        self.assertFalse(self.sample_recommendation.completed)
    
    def test_recommendation_to_dict(self):
        """Test converting recommendation to dictionary"""
        rec_dict = self.sample_recommendation.to_dict()
        
        self.assertEqual(rec_dict['recommendation_id'], "test_rec_001")
        self.assertEqual(rec_dict['priority'], "high")
        self.assertEqual(rec_dict['difficulty'], "moderate")
        self.assertIn('created_at', rec_dict)
        self.assertEqual(rec_dict['completed'], False)
    
    def test_recommendation_from_dict(self):
        """Test creating recommendation from dictionary"""
        rec_dict = self.sample_recommendation.to_dict()
        restored_rec = SecurityRecommendation.from_dict(rec_dict)
        
        self.assertEqual(restored_rec.recommendation_id, self.sample_recommendation.recommendation_id)
        self.assertEqual(restored_rec.priority, self.sample_recommendation.priority)
        self.assertEqual(restored_rec.difficulty, self.sample_recommendation.difficulty)

class TestRecommendationEngine(unittest.TestCase):
    """Test RecommendationEngine functionality"""
    
    def setUp(self):
        self.config = {
            'family_assistant': {
                'recommendation_engine': {
                    'max_recommendations': 10,
                    'default_expiry_days': 30
                }
            }
        }
        self.logger = Mock(spec=logging.Logger)
        self.engine = RecommendationEngine(self.config, self.logger)
        
        # Sample family profile
        self.family_profile = FamilyProfile(
            family_id="family_001",
            family_name="Test Family",
            members=[
                {
                    "member_id": "member_001",
                    "name": "Parent",
                    "age_group": "adult",
                    "tech_skill_level": "intermediate"
                },
                {
                    "member_id": "member_002",
                    "name": "Child",
                    "age_group": "child",
                    "tech_skill_level": "beginner"
                }
            ],
            devices=[
                {
                    "device_id": "device_001",
                    "device_type": "smartphone",
                    "owner": "member_001"
                },
                {
                    "device_id": "device_002",
                    "device_type": "tablet",
                    "owner": "member_002"
                }
            ],
            security_preferences={
                "data_protection": True,
                "child_safety": True
            },
            threat_tolerance="medium",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    def test_engine_initialization(self):
        """Test recommendation engine initialization"""
        self.assertIsInstance(self.engine.templates, dict)
        self.assertIn("password_manager", self.engine.templates)
        self.assertIn("router_security", self.engine.templates)
        self.assertIn("child_privacy", self.engine.templates)
    
    def test_generate_recommendations(self):
        """Test generating recommendations for a family"""
        recommendations = self.engine.generate_recommendations(self.family_profile)
        
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        
        # Check that recommendations are properly formed
        for rec in recommendations:
            self.assertIsInstance(rec, SecurityRecommendation)
            self.assertIsNotNone(rec.recommendation_id)
            self.assertIsNotNone(rec.title)
            self.assertIsNotNone(rec.description)
            self.assertIn(rec.priority, [Priority.CRITICAL, Priority.HIGH, Priority.MEDIUM, Priority.LOW])
            self.assertIn(rec.difficulty, [Difficulty.EASY, Difficulty.MODERATE, Difficulty.ADVANCED])
    
    def test_recommendations_include_child_safety(self):
        """Test that child safety recommendations are included for families with children"""
        recommendations = self.engine.generate_recommendations(self.family_profile)
        
        # Should include child privacy recommendations since family has children
        child_safety_recs = [rec for rec in recommendations if rec.category == "child_safety"]
        self.assertGreater(len(child_safety_recs), 0)
    
    def test_recommendations_exclude_child_safety_for_adults_only(self):
        """Test that child safety recommendations are excluded for adult-only families"""
        adult_only_profile = FamilyProfile(
            family_id="family_002",
            family_name="Adult Only Family",
            members=[
                {
                    "member_id": "member_001",
                    "name": "Adult 1",
                    "age_group": "adult",
                    "tech_skill_level": "advanced"
                },
                {
                    "member_id": "member_002",
                    "name": "Adult 2",
                    "age_group": "adult",
                    "tech_skill_level": "intermediate"
                }
            ],
            devices=[],
            security_preferences={},
            threat_tolerance="medium",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        recommendations = self.engine.generate_recommendations(adult_only_profile)
        child_safety_recs = [rec for rec in recommendations if rec.category == "child_safety"]
        self.assertEqual(len(child_safety_recs), 0)
    
    def test_priority_filtering(self):
        """Test filtering recommendations by priority"""
        # Generate some recommendations first
        self.engine.generate_recommendations(self.family_profile)
        
        high_priority_recs = self.engine.get_recommendations_by_priority(Priority.HIGH)
        self.assertIsInstance(high_priority_recs, list)
        
        # All returned recommendations should be high priority
        for rec in high_priority_recs:
            self.assertEqual(rec.priority, Priority.HIGH)
    
    def test_category_filtering(self):
        """Test filtering recommendations by category"""
        # Generate some recommendations first
        self.engine.generate_recommendations(self.family_profile)
        
        auth_recs = self.engine.get_recommendations_by_category("authentication")
        self.assertIsInstance(auth_recs, list)
        
        # All returned recommendations should be authentication category
        for rec in auth_recs:
            self.assertEqual(rec.category, "authentication")
    
    def test_mark_recommendation_completed(self):
        """Test marking recommendations as completed"""
        recommendations = self.engine.generate_recommendations(self.family_profile)
        
        if recommendations:
            rec_id = recommendations[0].recommendation_id
            result = self.engine.mark_recommendation_completed(rec_id)
            
            self.assertTrue(result)
            self.assertTrue(self.engine.recommendations[rec_id].completed)
    
    def test_mark_nonexistent_recommendation_completed(self):
        """Test marking non-existent recommendation as completed"""
        result = self.engine.mark_recommendation_completed("nonexistent_id")
        self.assertFalse(result)
    
    def test_get_active_recommendations(self):
        """Test getting active (non-completed, non-expired) recommendations"""
        recommendations = self.engine.generate_recommendations(self.family_profile)
        
        # All should be active initially
        active_recs = self.engine.get_active_recommendations()
        self.assertEqual(len(active_recs), len(recommendations))
        
        # Mark one as completed
        if recommendations:
            rec_id = recommendations[0].recommendation_id
            self.engine.mark_recommendation_completed(rec_id)
            
            active_recs = self.engine.get_active_recommendations()
            self.assertEqual(len(active_recs), len(recommendations) - 1)
    
    def test_cleanup_expired_recommendations(self):
        """Test cleaning up expired recommendations"""
        # Generate recommendations
        recommendations = self.engine.generate_recommendations(self.family_profile)
        
        # Manually expire one recommendation
        if recommendations:
            rec_id = recommendations[0].recommendation_id
            self.engine.recommendations[rec_id].expires_at = datetime.now() - timedelta(days=1)
            
            # Clean up expired recommendations
            cleaned_count = self.engine.cleanup_expired_recommendations()
            
            self.assertEqual(cleaned_count, 1)
            self.assertNotIn(rec_id, self.engine.recommendations)
    
    def test_average_skill_level_calculation(self):
        """Test calculation of average family skill level"""
        # Test with mixed skill levels
        avg_skill = self.engine._get_average_skill_level(self.family_profile)
        self.assertIn(avg_skill, ["beginner", "intermediate", "advanced"])
        
        # Test with all beginners
        beginner_profile = FamilyProfile(
            family_id="family_003",
            family_name="Beginner Family",
            members=[
                {"member_id": "m1", "tech_skill_level": "beginner"},
                {"member_id": "m2", "tech_skill_level": "beginner"}
            ],
            devices=[],
            security_preferences={},
            threat_tolerance="low",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        avg_skill = self.engine._get_average_skill_level(beginner_profile)
        self.assertEqual(avg_skill, "beginner")
    
    def test_step_simplification(self):
        """Test simplification of steps for beginner users"""
        original_steps = [
            "Access your router's admin panel",
            "Set WiFi security to WPA3",
            "Create a strong password"
        ]
        
        simplified_steps = self.engine._simplify_steps(original_steps)
        
        self.assertEqual(len(simplified_steps), len(original_steps))
        # Check that admin panel step has additional explanation
        admin_step = next((step for step in simplified_steps if "admin panel" in step), None)
        self.assertIsNotNone(admin_step)
        self.assertIn("192.168.1.1", admin_step)

if __name__ == '__main__':
    unittest.main()