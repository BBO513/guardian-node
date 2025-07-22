"""
Family Assistant Data Models
Defines data structures for family profiles, devices, and security recommendations
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional

@dataclass
class FamilyMember:
    """Represents a family member with their security profile"""
    member_id: str
    name: str
    age_group: str  # "child", "teen", "adult"
    tech_skill_level: str  # "beginner", "intermediate", "advanced"
    devices: List[str] = field(default_factory=list)  # Device IDs
    special_needs: List[str] = field(default_factory=list)  # Accessibility, learning differences, etc.
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class SecurityStatus:
    """Security status for a device or system"""
    status: str  # "secure", "warning", "critical"
    last_checked: datetime = field(default_factory=datetime.now)
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

@dataclass
class Device:
    """Represents a family device with security information"""
    device_id: str
    device_type: str  # "smartphone", "tablet", "computer", "iot"
    os_type: str
    os_version: str
    owner: str  # Family member ID
    security_status: SecurityStatus = field(default_factory=lambda: SecurityStatus("unknown"))
    last_assessed: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class SecurityPreferences:
    """Family security preferences and settings"""
    threat_tolerance: str = "medium"  # "low", "medium", "high"
    auto_recommendations: bool = True
    child_safe_mode: bool = True
    notification_level: str = "normal"  # "minimal", "normal", "detailed"
    privacy_level: str = "high"  # "low", "medium", "high"

@dataclass
class FamilyProfile:
    """Complete family profile with members, devices, and preferences"""
    family_id: str
    family_name: str
    members: List[FamilyMember] = field(default_factory=list)
    devices: List[Device] = field(default_factory=list)
    security_preferences: SecurityPreferences = field(default_factory=SecurityPreferences)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def get_member_by_id(self, member_id: str) -> Optional[FamilyMember]:
        """Get family member by ID"""
        for member in self.members:
            if member.member_id == member_id:
                return member
        return None
    
    def get_device_by_id(self, device_id: str) -> Optional[Device]:
        """Get device by ID"""
        for device in self.devices:
            if device.device_id == device_id:
                return device
        return None
    
    def get_devices_by_owner(self, member_id: str) -> List[Device]:
        """Get all devices owned by a family member"""
        return [device for device in self.devices if device.owner == member_id]
    
    def get_children(self) -> List[FamilyMember]:
        """Get all child members"""
        return [member for member in self.members if member.age_group == "child"]
    
    def get_teens(self) -> List[FamilyMember]:
        """Get all teen members"""
        return [member for member in self.members if member.age_group == "teen"]
    
    def get_adults(self) -> List[FamilyMember]:
        """Get all adult members"""
        return [member for member in self.members if member.age_group == "adult"]

@dataclass
class SecurityRecommendation:
    """Security recommendation for family"""
    recommendation_id: str
    title: str
    description: str
    priority: str  # "critical", "high", "medium", "low"
    difficulty: str  # "easy", "moderate", "advanced"
    estimated_time: str
    steps: List[str] = field(default_factory=list)
    applicable_devices: List[str] = field(default_factory=list)
    family_members: List[str] = field(default_factory=list)
    category: str = "general"  # "device", "network", "education", "general"
    created_at: datetime = field(default_factory=datetime.now)
    completed: bool = False
    completed_at: Optional[datetime] = None

@dataclass
class FamilyContext:
    """Context for family assistant interactions"""
    family_id: str
    session_id: str
    current_member: Optional[str] = None
    interaction_history: List[Dict[str, Any]] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    
    def add_interaction(self, interaction_type: str, data: Dict[str, Any]):
        """Add an interaction to the history"""
        self.interaction_history.append({
            'type': interaction_type,
            'data': data,
            'timestamp': datetime.now()
        })
        self.last_activity = datetime.now()
        
        # Keep only last 50 interactions
        if len(self.interaction_history) > 50:
            self.interaction_history = self.interaction_history[-50:]

@dataclass
class FamilyAnalysisResult:
    """Result of family security analysis"""
    family_id: str
    status: str  # "secure", "warning", "critical"
    overall_score: float  # 0-100
    findings: List[str] = field(default_factory=list)
    recommendations: List[SecurityRecommendation] = field(default_factory=list)
    device_statuses: Dict[str, SecurityStatus] = field(default_factory=dict)
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    next_analysis_due: Optional[datetime] = None