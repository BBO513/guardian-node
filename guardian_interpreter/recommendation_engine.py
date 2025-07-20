#!/usr/bin/env python3
"""
Family Cybersecurity Recommendation Engine
Generates personalized security recommendations based on family profiles and threat analysis
"""

import json
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
from pathlib import Path
from enum import Enum

class Priority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Difficulty(Enum):
    EASY = "easy"
    MODERATE = "moderate"
    ADVANCED = "advanced"

@dataclass
class SecurityRecommendation:
    """Data model for security recommendations"""
    recommendation_id: str
    title: str
    description: str
    priority: Priority
    difficulty: Difficulty
    estimated_time: str
    steps: List[str]
    applicable_devices: List[str]
    family_members: List[str]
    category: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    completed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['priority'] = self.priority.value
        data['difficulty'] = self.difficulty.value
        data['created_at'] = self.created_at.isoformat()
        if self.expires_at:
            data['expires_at'] = self.expires_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SecurityRecommendation':
        """Create from dictionary"""
        data['priority'] = Priority(data['priority'])
        data['difficulty'] = Difficulty(data['difficulty'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('expires_at'):
            data['expires_at'] = datetime.fromisoformat(data['expires_at'])
        return cls(**data)

@dataclass
class FamilyProfile:
    """Family profile for personalized recommendations"""
    family_id: str
    family_name: str
    members: List[Dict[str, Any]]
    devices: List[Dict[str, Any]]
    security_preferences: Dict[str, Any]
    threat_tolerance: str  # "low", "medium", "high"
    created_at: datetime
    updated_at: datetime

class RecommendationEngine:
    """
    Core recommendation engine that generates personalized cybersecurity recommendations
    """
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.recommendations: Dict[str, SecurityRecommendation] = {}
        
        # Load recommendation templates
        self._load_recommendation_templates()
        
    def _load_recommendation_templates(self):
        """Load predefined recommendation templates"""
        self.templates = {
            "password_manager": {
                "title": "Set up a family password manager",
                "description": "Use a password manager to create and store unique, strong passwords for all family accounts",
                "category": "authentication",
                "priority": Priority.HIGH,
                "difficulty": Difficulty.MODERATE,
                "estimated_time": "30-45 minutes",
                "steps": [
                    "Research family-friendly password managers (Bitwarden, 1Password, etc.)",
                    "Create a family account with your chosen password manager",
                    "Install the password manager app on all family devices",
                    "Generate strong, unique passwords for important accounts",
                    "Teach family members how to use the password manager",
                    "Enable two-factor authentication where possible"
                ]
            },
            "router_security": {
                "title": "Secure your home WiFi router",
                "description": "Update router settings to protect your home network from unauthorized access",
                "category": "network",
                "priority": Priority.HIGH,
                "difficulty": Difficulty.MODERATE,
                "estimated_time": "20-30 minutes",
                "steps": [
                    "Access your router's admin panel (usually 192.168.1.1 or 192.168.0.1)",
                    "Change the default admin username and password",
                    "Update the WiFi network name (SSID) to something non-identifying",
                    "Set WiFi security to WPA3 (or WPA2 if WPA3 isn't available)",
                    "Create a strong WiFi password (12+ characters)",
                    "Disable WPS (WiFi Protected Setup)",
                    "Enable automatic firmware updates if available"
                ]
            },
            "device_updates": {
                "title": "Enable automatic security updates",
                "description": "Ensure all family devices receive important security patches automatically",
                "category": "device_security",
                "priority": Priority.MEDIUM,
                "difficulty": Difficulty.EASY,
                "estimated_time": "10-15 minutes per device",
                "steps": [
                    "Check each family device for available updates",
                    "Enable automatic updates for operating systems",
                    "Enable automatic updates for important apps",
                    "Set devices to install security updates immediately",
                    "Schedule regular update checks for devices that don't auto-update"
                ]
            },
            "child_privacy": {
                "title": "Review children's app privacy settings",
                "description": "Adjust privacy settings on apps and services used by children to protect their personal information",
                "category": "child_safety",
                "priority": Priority.HIGH,
                "difficulty": Difficulty.MODERATE,
                "estimated_time": "15-20 minutes per child",
                "steps": [
                    "Review privacy settings on social media apps",
                    "Disable location sharing in unnecessary apps",
                    "Turn off data collection for advertising",
                    "Set profiles to private/friends-only where appropriate",
                    "Review and limit app permissions",
                    "Discuss privacy settings with your children"
                ]
            },
            "backup_strategy": {
                "title": "Create a family data backup plan",
                "description": "Protect important family photos, documents, and data with regular backups",
                "category": "data_protection",
                "priority": Priority.MEDIUM,
                "difficulty": Difficulty.MODERATE,
                "estimated_time": "45-60 minutes",
                "steps": [
                    "Identify important family data (photos, documents, etc.)",
                    "Choose backup solutions (cloud storage, external drives)",
                    "Set up automatic backups for critical data",
                    "Test backup restoration process",
                    "Create a backup schedule and stick to it",
                    "Store physical backups in a safe location"
                ]
            }
        }
    
    def generate_recommendations(self, family_profile: FamilyProfile) -> List[SecurityRecommendation]:
        """
        Generate personalized recommendations based on family profile
        """
        recommendations = []
        current_time = datetime.now()
        
        # Analyze family profile to determine relevant recommendations
        relevant_templates = self._filter_templates_by_profile(family_profile)
        
        for template_key, template in relevant_templates.items():
            # Create personalized recommendation
            rec_id = f"{family_profile.family_id}_{template_key}_{int(current_time.timestamp())}"
            
            # Customize for family
            customized_template = self._customize_template(template, family_profile)
            
            recommendation = SecurityRecommendation(
                recommendation_id=rec_id,
                title=customized_template["title"],
                description=customized_template["description"],
                priority=customized_template["priority"],
                difficulty=customized_template["difficulty"],
                estimated_time=customized_template["estimated_time"],
                steps=customized_template["steps"],
                applicable_devices=self._get_applicable_devices(template, family_profile),
                family_members=self._get_applicable_members(template, family_profile),
                category=customized_template["category"],
                created_at=current_time,
                expires_at=current_time + timedelta(days=30)  # Recommendations expire after 30 days
            )
            
            recommendations.append(recommendation)
            self.recommendations[rec_id] = recommendation
        
        # Sort by priority and difficulty
        recommendations = self._prioritize_recommendations(recommendations, family_profile)
        
        self.logger.info(f"Generated {len(recommendations)} recommendations for family {family_profile.family_id}")
        return recommendations
    
    def _filter_templates_by_profile(self, family_profile: FamilyProfile) -> Dict[str, Dict]:
        """Filter recommendation templates based on family profile"""
        relevant_templates = {}
        
        # Always include basic security recommendations
        relevant_templates["password_manager"] = self.templates["password_manager"]
        relevant_templates["router_security"] = self.templates["router_security"]
        relevant_templates["device_updates"] = self.templates["device_updates"]
        
        # Include child-specific recommendations if family has children
        has_children = any(member.get("age_group") in ["child", "teen"] for member in family_profile.members)
        if has_children:
            relevant_templates["child_privacy"] = self.templates["child_privacy"]
        
        # Include backup recommendations for families with high security preferences
        if family_profile.security_preferences.get("data_protection", False):
            relevant_templates["backup_strategy"] = self.templates["backup_strategy"]
        
        return relevant_templates
    
    def _customize_template(self, template: Dict, family_profile: FamilyProfile) -> Dict:
        """Customize recommendation template for specific family"""
        customized = template.copy()
        
        # Adjust difficulty based on family tech skill level
        avg_skill_level = self._get_average_skill_level(family_profile)
        if avg_skill_level == "beginner" and template["difficulty"] == Difficulty.ADVANCED:
            customized["difficulty"] = Difficulty.MODERATE
            customized["steps"] = self._simplify_steps(template["steps"])
        
        # Adjust priority based on threat tolerance
        if family_profile.threat_tolerance == "low":
            if template["priority"] == Priority.MEDIUM:
                customized["priority"] = Priority.HIGH
        elif family_profile.threat_tolerance == "high":
            if template["priority"] == Priority.HIGH:
                customized["priority"] = Priority.MEDIUM
        
        return customized
    
    def _get_average_skill_level(self, family_profile: FamilyProfile) -> str:
        """Calculate average technical skill level of family"""
        skill_levels = [member.get("tech_skill_level", "beginner") for member in family_profile.members]
        skill_weights = {"beginner": 1, "intermediate": 2, "advanced": 3}
        
        if not skill_levels:
            return "beginner"
        
        avg_weight = sum(skill_weights.get(level, 1) for level in skill_levels) / len(skill_levels)
        
        if avg_weight <= 1.3:
            return "beginner"
        elif avg_weight <= 2.3:
            return "intermediate"
        else:
            return "advanced"
    
    def _simplify_steps(self, steps: List[str]) -> List[str]:
        """Simplify steps for beginner users"""
        simplified = []
        for step in steps:
            # Add more detailed explanations for complex steps
            if "admin panel" in step.lower():
                simplified.append(step + " (Look for a web address like 192.168.1.1 in your router manual)")
            elif "wpa3" in step.lower():
                simplified.append(step + " (Choose the strongest security option available)")
            else:
                simplified.append(step)
        return simplified
    
    def _get_applicable_devices(self, template: Dict, family_profile: FamilyProfile) -> List[str]:
        """Get list of devices this recommendation applies to"""
        category = template["category"]
        applicable_devices = []
        
        for device in family_profile.devices:
            device_type = device.get("device_type", "")
            
            if category == "network" and device_type in ["router", "modem"]:
                applicable_devices.append(device.get("device_id", ""))
            elif category in ["device_security", "authentication"] and device_type in ["smartphone", "tablet", "computer"]:
                applicable_devices.append(device.get("device_id", ""))
            elif category == "child_safety" and device.get("owner") in [m.get("member_id") for m in family_profile.members if m.get("age_group") in ["child", "teen"]]:
                applicable_devices.append(device.get("device_id", ""))
        
        return applicable_devices
    
    def _get_applicable_members(self, template: Dict, family_profile: FamilyProfile) -> List[str]:
        """Get list of family members this recommendation applies to"""
        category = template["category"]
        applicable_members = []
        
        for member in family_profile.members:
            member_id = member.get("member_id", "")
            age_group = member.get("age_group", "adult")
            
            if category == "child_safety" and age_group in ["child", "teen"]:
                applicable_members.append(member_id)
            elif category in ["authentication", "network", "device_security", "data_protection"]:
                applicable_members.append(member_id)
        
        return applicable_members
    
    def _prioritize_recommendations(self, recommendations: List[SecurityRecommendation], family_profile: FamilyProfile) -> List[SecurityRecommendation]:
        """Sort recommendations by priority and difficulty"""
        priority_order = {Priority.CRITICAL: 0, Priority.HIGH: 1, Priority.MEDIUM: 2, Priority.LOW: 3}
        difficulty_order = {Difficulty.EASY: 0, Difficulty.MODERATE: 1, Difficulty.ADVANCED: 2}
        
        return sorted(recommendations, key=lambda r: (priority_order[r.priority], difficulty_order[r.difficulty]))
    
    def get_recommendations_by_priority(self, priority: Priority) -> List[SecurityRecommendation]:
        """Get all recommendations filtered by priority"""
        return [rec for rec in self.recommendations.values() if rec.priority == priority and not rec.completed]
    
    def get_recommendations_by_category(self, category: str) -> List[SecurityRecommendation]:
        """Get all recommendations filtered by category"""
        return [rec for rec in self.recommendations.values() if rec.category == category and not rec.completed]
    
    def mark_recommendation_completed(self, recommendation_id: str) -> bool:
        """Mark a recommendation as completed"""
        if recommendation_id in self.recommendations:
            self.recommendations[recommendation_id].completed = True
            self.logger.info(f"Recommendation {recommendation_id} marked as completed")
            return True
        return False
    
    def get_active_recommendations(self) -> List[SecurityRecommendation]:
        """Get all active (non-completed, non-expired) recommendations"""
        current_time = datetime.now()
        return [
            rec for rec in self.recommendations.values()
            if not rec.completed and (not rec.expires_at or rec.expires_at > current_time)
        ]
    
    def cleanup_expired_recommendations(self) -> int:
        """Remove expired recommendations and return count of removed items"""
        current_time = datetime.now()
        expired_ids = [
            rec_id for rec_id, rec in self.recommendations.items()
            if rec.expires_at and rec.expires_at <= current_time
        ]
        
        for rec_id in expired_ids:
            del self.recommendations[rec_id]
        
        self.logger.info(f"Cleaned up {len(expired_ids)} expired recommendations")
        return len(expired_ids)