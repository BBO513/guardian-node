"""
Family Assistant Manager
Central coordinator for all family cybersecurity assistance functionality
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# Import Guardian components
try:
    from guardian_interpreter.network_security import AuditLogger
    from guardian_interpreter.data_persistence import FamilyDataStore
    from guardian_interpreter.recommendation_engine import RecommendationEngine
    from guardian_interpreter.family_response_formatter import FamilyResponseFormatter
    from guardian_interpreter.family_llm_prompts import FamilyPromptManager as FamilyLLMPrompts
    from guardian_interpreter.performance_optimizer import get_optimizer
except ImportError as e:
    print(f"Warning: Could not import some Guardian components: {e}")
    # Create minimal fallback classes
    class AuditLogger:
        def __init__(self, *args, **kwargs): pass
        def log_system_event(self, *args, **kwargs): pass
        def log_user_action(self, *args, **kwargs): pass
        def log_skill_execution(self, *args, **kwargs): pass
    
    class FamilyDataStore:
        def __init__(self, *args, **kwargs): pass
    
    class RecommendationEngine:
        def __init__(self, *args, **kwargs): pass
        def generate_family_recommendations(self, *args, **kwargs): return []
    
    class FamilyResponseFormatter:
        def __init__(self): pass
        def format_for_family(self, text, context=None): return text
    
    class FamilyLLMPrompts:
        def __init__(self, *args, **kwargs): pass
    
    def get_optimizer(): return None

# Import family models
try:
    from guardian_interpreter.family_assistant.models import (
        FamilyProfile, FamilyMember, Device, SecurityRecommendation,
        FamilyContext, FamilyAnalysisResult, SecurityStatus
    )
except ImportError as e:
    print(f"Warning: Could not import family models: {e}")
    # Create minimal fallback classes
    from dataclasses import dataclass
    from typing import List
    from datetime import datetime
    
    @dataclass
    class FamilyProfile:
        family_id: str = "default"
        family_name: str = "Default Family"
        members: List = None
        devices: List = None
        
        def __post_init__(self):
            if self.members is None: self.members = []
            if self.devices is None: self.devices = []
        
        def get_children(self): return []
    
    @dataclass
    class FamilyMember:
        member_id: str = ""
        name: str = ""
        age_group: str = "adult"
    
    @dataclass
    class Device:
        device_id: str = ""
        device_type: str = ""
        os_version: str = ""
    
    @dataclass
    class SecurityRecommendation:
        recommendation_id: str = ""
        title: str = ""
        description: str = ""
        priority: str = "medium"
    
    @dataclass
    class FamilyContext:
        family_id: str = ""
        session_id: str = ""
        interactions: List = None
        
        def __post_init__(self):
            if self.interactions is None: self.interactions = []
        
        def add_interaction(self, interaction_type, data): pass
    
    @dataclass
    class FamilyAnalysisResult:
        family_id: str = ""
        status: str = "unknown"
        overall_score: float = 0.0
        findings: List = None
        recommendations: List = None
        device_statuses: dict = None
        next_analysis_due: datetime = None
        
        def __post_init__(self):
            if self.findings is None: self.findings = []
            if self.recommendations is None: self.recommendations = []
            if self.device_statuses is None: self.device_statuses = {}
    
    @dataclass
    class SecurityStatus:
        status: str = "unknown"
        issues: List = None
        recommendations: List = None
        
        def __post_init__(self):
            if self.issues is None: self.issues = []
            if self.recommendations is None: self.recommendations = []

class FamilyAssistantManager:
    """
    Central coordinator for family cybersecurity assistance
    Integrates all family assistant components with Guardian Interpreter
    """
    
    def __init__(self, config: Dict[str, Any] = None, logger: logging.Logger = None, 
                 audit_logger: AuditLogger = None):
        self.config = config or {}
        self.logger = logger or logging.getLogger(__name__)
        self.audit_logger = audit_logger
        
        # Initialize components
        self._initialize_components()
        
        # Active contexts for family sessions
        self.active_contexts: Dict[str, FamilyContext] = {}
        
        # Skills registry for family skills
        self.family_skills = {}
        
        self.logger.info("FamilyAssistantManager initialized")
    
    def _initialize_components(self):
        """Initialize all family assistant components"""
        try:
            # Data persistence
            self.data_store = FamilyDataStore(self.config, self.logger)
            
            # Recommendation engine
            self.recommendation_engine = RecommendationEngine(self.config, self.logger)
            
            # Response formatter
            self.response_formatter = FamilyResponseFormatter()
            
            # LLM prompts
            self.llm_prompts = FamilyLLMPrompts()
            
            # Performance optimizer
            self.optimizer = get_optimizer()
            
            self.logger.info("Family assistant components initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize family assistant components: {e}")
            raise
    
    def register_family_skill(self, skill_name: str, skill_instance):
        """Register a family skill with the manager"""
        self.family_skills[skill_name] = skill_instance
        self.logger.info(f"Registered family skill: {skill_name}")
        
        if self.audit_logger:
            self.audit_logger.log_system_event("Family skill registered", {
                'skill_name': skill_name
            })
    
    def process_family_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a family cybersecurity query and return response
        
        Args:
            query: Natural language query from family member
            context: Additional context including family profile, member info, etc.
            
        Returns:
            Dict containing response, confidence, and metadata
        """
        try:
            # Log the query
            if self.audit_logger:
                self.audit_logger.log_user_action("Family query processed", {
                    'query_length': len(query),
                    'has_context': bool(context)
                })
            
            # Get or create family context
            family_profile = context.get('family_profile') if context else None
            family_context = self._get_or_create_context(family_profile)
            
            # Add query to interaction history
            family_context.add_interaction('query', {
                'query': query,
                'context_keys': list(context.keys()) if context else []
            })
            
            # Determine which skill should handle the query
            skill_name, confidence = self._route_query_to_skill(query, context)
            
            if skill_name and skill_name in self.family_skills:
                # Execute the appropriate family skill
                skill_result = self._execute_family_skill(skill_name, query, context)
                
                # Format response for family-friendly output
                formatted_response = self.response_formatter.format_for_family(
                    skill_result.get('response', ''),
                    context or {}
                )
                
                response = {
                    'response': formatted_response,
                    'confidence': confidence,
                    'skill_used': skill_name,
                    'recommendations': skill_result.get('recommendations', []),
                    'follow_up_questions': skill_result.get('follow_up_questions', []),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # Fallback to general family cybersecurity guidance
                response = self._generate_fallback_response(query, context)
            
            # Add response to interaction history
            family_context.add_interaction('response', {
                'skill_used': response.get('skill_used'),
                'confidence': response.get('confidence'),
                'response_length': len(response.get('response', ''))
            })
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing family query: {e}")
            return {
                'response': "I'm sorry, I encountered an error processing your question. Please try again or ask a different question.",
                'confidence': 0.0,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def analyze_family_security(self, family_profile: Dict[str, Any]) -> FamilyAnalysisResult:
        """
        Analyze overall family security posture
        
        Args:
            family_profile: Family profile data
            
        Returns:
            FamilyAnalysisResult with security analysis
        """
        try:
            if self.audit_logger:
                self.audit_logger.log_system_event("Family security analysis started", {
                    'family_id': family_profile.get('family_id', 'unknown')
                })
            
            # Convert dict to FamilyProfile object if needed
            if isinstance(family_profile, dict):
                profile = self._dict_to_family_profile(family_profile)
            else:
                profile = family_profile
            
            # Initialize analysis result
            analysis = FamilyAnalysisResult(
                family_id=profile.family_id,
                status="secure",
                overall_score=100.0
            )
            
            # Analyze each device
            device_issues = []
            for device in profile.devices:
                device_status = self._analyze_device_security(device, profile)
                analysis.device_statuses[device.device_id] = device_status
                
                if device_status.status == "critical":
                    analysis.status = "critical"
                    analysis.overall_score -= 30
                elif device_status.status == "warning" and analysis.status != "critical":
                    analysis.status = "warning"
                    analysis.overall_score -= 15
                
                device_issues.extend(device_status.issues)
            
            # Analyze family configuration
            config_issues = self._analyze_family_configuration(profile)
            analysis.findings.extend(config_issues)
            
            # Generate recommendations
            recommendations = self.recommendation_engine.generate_family_recommendations(
                profile, analysis.device_statuses
            )
            analysis.recommendations = recommendations
            
            # Set next analysis due date
            analysis.next_analysis_due = datetime.now() + timedelta(days=7)
            
            # Ensure score doesn't go below 0
            analysis.overall_score = max(0.0, analysis.overall_score)
            
            if self.audit_logger:
                self.audit_logger.log_system_event("Family security analysis completed", {
                    'family_id': profile.family_id,
                    'status': analysis.status,
                    'score': analysis.overall_score,
                    'recommendations_count': len(analysis.recommendations)
                })
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing family security: {e}")
            return FamilyAnalysisResult(
                family_id=family_profile.get('family_id', 'unknown'),
                status="critical",
                overall_score=0.0,
                findings=[f"Analysis failed: {str(e)}"]
            )
    
    def get_family_recommendations(self, family_profile: Dict[str, Any]) -> List[SecurityRecommendation]:
        """
        Get personalized security recommendations for family
        
        Args:
            family_profile: Family profile data
            
        Returns:
            List of SecurityRecommendation objects
        """
        try:
            # Convert dict to FamilyProfile object if needed
            if isinstance(family_profile, dict):
                profile = self._dict_to_family_profile(family_profile)
            else:
                profile = family_profile
            
            # Generate recommendations using the recommendation engine
            recommendations = self.recommendation_engine.generate_family_recommendations(profile)
            
            if self.audit_logger:
                self.audit_logger.log_system_event("Family recommendations generated", {
                    'family_id': profile.family_id,
                    'recommendations_count': len(recommendations)
                })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating family recommendations: {e}")
            return []
    
    def format_family_response(self, technical_response: str, context: Dict[str, Any] = None) -> str:
        """
        Format technical response for family-friendly output
        
        Args:
            technical_response: Technical cybersecurity response
            context: Context including target audience, tech level, etc.
            
        Returns:
            Family-friendly formatted response
        """
        try:
            return self.response_formatter.format_for_family(technical_response, context or {})
        except Exception as e:
            self.logger.error(f"Error formatting family response: {e}")
            return technical_response  # Return original if formatting fails
    
    def manage_family_context(self, family_id: str) -> FamilyContext:
        """
        Get or create family context for session management
        
        Args:
            family_id: Family identifier
            
        Returns:
            FamilyContext object
        """
        if family_id not in self.active_contexts:
            self.active_contexts[family_id] = FamilyContext(
                family_id=family_id,
                session_id=str(uuid.uuid4())
            )
            
            if self.audit_logger:
                self.audit_logger.log_system_event("Family context created", {
                    'family_id': family_id
                })
        
        return self.active_contexts[family_id]
    
    def run_family_skill(self, skill_name: str, *args, **kwargs) -> Dict[str, Any]:
        """
        Execute a specific family skill
        
        Args:
            skill_name: Name of the skill to execute
            *args: Positional arguments for the skill
            **kwargs: Keyword arguments for the skill
            
        Returns:
            Skill execution result
        """
        try:
            if skill_name not in self.family_skills:
                raise ValueError(f"Family skill not found: {skill_name}")
            
            if self.audit_logger:
                self.audit_logger.log_skill_execution(skill_name, list(args))
            
            skill = self.family_skills[skill_name]
            result = skill.run(*args, **kwargs)
            
            return {
                'success': True,
                'result': result,
                'skill_name': skill_name,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error executing family skill {skill_name}: {e}")
            return {
                'success': False,
                'error': str(e),
                'skill_name': skill_name,
                'timestamp': datetime.now().isoformat()
            }
    
    def _get_or_create_context(self, family_profile: Optional[Dict[str, Any]]) -> FamilyContext:
        """Get or create family context"""
        family_id = family_profile.get('family_id', 'default') if family_profile else 'default'
        return self.manage_family_context(family_id)
    
    def _route_query_to_skill(self, query: str, context: Dict[str, Any] = None) -> Tuple[Optional[str], float]:
        """
        Route query to appropriate family skill
        
        Returns:
            Tuple of (skill_name, confidence)
        """
        query_lower = query.lower()
        
        # Simple keyword-based routing (can be enhanced with ML)
        if any(word in query_lower for word in ['threat', 'attack', 'virus', 'malware', 'scam']):
            return 'threat_analysis_skill', 0.8
        elif any(word in query_lower for word in ['device', 'phone', 'tablet', 'computer', 'ipad']):
            return 'device_guidance_skill', 0.8
        elif any(word in query_lower for word in ['child', 'kid', 'teach', 'education', 'learn']):
            return 'child_education_skill', 0.8
        elif any(word in query_lower for word in ['family', 'general', 'overview', 'help']):
            return 'family_cyber_skills', 0.7
        else:
            return 'family_cyber_skills', 0.5  # Default to general family skills
    
    def _execute_family_skill(self, skill_name: str, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a family skill and return structured result"""
        try:
            skill = self.family_skills[skill_name]
            
            # Execute skill with query and context
            if hasattr(skill, 'run'):
                result = skill.run(query, context=context)
            else:
                result = skill.run()
            
            # Ensure result is a dictionary
            if isinstance(result, str):
                return {'response': result}
            elif isinstance(result, dict):
                return result
            else:
                return {'response': str(result)}
                
        except Exception as e:
            self.logger.error(f"Error executing family skill {skill_name}: {e}")
            return {'response': f"Error executing {skill_name}: {str(e)}"}
    
    def _generate_fallback_response(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate fallback response when no specific skill matches"""
        fallback_responses = [
            "I understand you're asking about cybersecurity. Let me provide some general family safety guidance.",
            "That's a great question about digital safety! Here are some key points to consider:",
            "For family cybersecurity, it's important to focus on the basics first."
        ]
        
        import random
        response = random.choice(fallback_responses)
        
        return {
            'response': response + " You might want to ask about specific devices, current threats, or child education for more targeted advice.",
            'confidence': 0.3,
            'skill_used': 'fallback',
            'follow_up_questions': [
                "What devices does your family use?",
                "Are you concerned about any specific threats?",
                "Would you like help teaching children about online safety?"
            ],
            'timestamp': datetime.now().isoformat()
        }
    
    def _dict_to_family_profile(self, profile_dict: Dict[str, Any]) -> FamilyProfile:
        """Convert dictionary to FamilyProfile object"""
        # This is a simplified conversion - in production you'd want more robust handling
        return FamilyProfile(
            family_id=profile_dict.get('family_id', 'unknown'),
            family_name=profile_dict.get('family_name', 'Unknown Family'),
            members=[],  # Would convert member dicts to FamilyMember objects
            devices=[]   # Would convert device dicts to Device objects
        )
    
    def _analyze_device_security(self, device: Device, family_profile: FamilyProfile) -> SecurityStatus:
        """Analyze security status of a specific device"""
        issues = []
        recommendations = []
        status = "secure"
        
        # Basic device security checks
        if device.os_version == "unknown" or not device.os_version:
            issues.append(f"{device.device_type} OS version unknown")
            recommendations.append("Check and update device operating system")
            status = "warning"
        
        # Add more device-specific checks here
        
        return SecurityStatus(
            status=status,
            issues=issues,
            recommendations=recommendations
        )
    
    def _analyze_family_configuration(self, family_profile: FamilyProfile) -> List[str]:
        """Analyze family configuration for security issues"""
        issues = []
        
        # Check if family has children but no parental controls mentioned
        children = family_profile.get_children()
        if children and not any('parental' in str(device.device_type).lower() for device in family_profile.devices):
            issues.append("Family has children but no parental control devices detected")
        
        # Add more family configuration checks here
        
        return issues
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for the family assistant"""
        return {
            'active_contexts': len(self.active_contexts),
            'registered_skills': len(self.family_skills),
            'optimizer_stats': self.optimizer.get_performance_metrics() if self.optimizer else {},
            'timestamp': datetime.now().isoformat()
        }