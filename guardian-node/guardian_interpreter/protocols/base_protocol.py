"""
Base Protocol Module Template
Provides standard interface for all protocol analysis modules
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime

class BaseProtocolModule(ABC):
    """
    Abstract base class for protocol analysis modules
    All protocol modules should inherit from this class
    """
    
    def __init__(self):
        self.name = "Base Protocol"
        self.version = "1.0.0"
        self.author = "Guardian Team"
        self.description = "Base protocol analysis module"
        self.family_friendly = True
        self.supported_protocols = []
    
    @abstractmethod
    def analyze(self, target: str = None, **kwargs) -> Dict[str, Any]:
        """
        Perform protocol analysis
        
        Args:
            target: Target for analysis (IP, network, device, etc.)
            **kwargs: Additional analysis parameters
            
        Returns:
            Dict containing:
            - status: "secure", "warning", "critical", "error"
            - findings: List of findings with severity and description
            - recommendations: List of actionable recommendations
            - technical_details: Dict of technical information
        """
        pass
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get module metadata
        
        Returns:
            Dict containing module information
        """
        pass
    
    def _create_finding(self, severity: str, title: str, description: str, 
                       recommendation: str = None, technical_info: Dict = None) -> Dict[str, Any]:
        """
        Helper method to create standardized finding
        
        Args:
            severity: "info", "low", "medium", "high", "critical"
            title: Short title for the finding
            description: Detailed description
            recommendation: Suggested action (optional)
            technical_info: Technical details (optional)
            
        Returns:
            Standardized finding dictionary
        """
        finding = {
            'severity': severity,
            'title': title,
            'description': description,
            'timestamp': datetime.now().isoformat()
        }
        
        if recommendation:
            finding['recommendation'] = recommendation
        
        if technical_info:
            finding['technical_info'] = technical_info
        
        return finding
    
    def _determine_overall_status(self, findings: List[Dict[str, Any]]) -> str:
        """
        Determine overall status based on findings
        
        Args:
            findings: List of findings
            
        Returns:
            Overall status string
        """
        if not findings:
            return "secure"
        
        # Check for critical findings
        for finding in findings:
            severity = finding.get('severity', 'info').lower()
            if severity == 'critical':
                return "critical"
        
        # Check for high severity findings
        for finding in findings:
            severity = finding.get('severity', 'info').lower()
            if severity == 'high':
                return "critical"
        
        # Check for medium severity findings
        for finding in findings:
            severity = finding.get('severity', 'info').lower()
            if severity == 'medium':
                return "warning"
        
        # Only low or info findings
        return "warning" if findings else "secure"


def get_metadata():
    """
    Template metadata function - should be implemented by each protocol module
    """
    return {
        'name': 'Base Protocol Module',
        'description': 'Template for protocol analysis modules',
        'version': '1.0.0',
        'author': 'Guardian Team',
        'family_friendly': True,
        'supported_protocols': []
    }

def analyze(target: str = None, **kwargs) -> Dict[str, Any]:
    """
    Template analyze function - should be implemented by each protocol module
    """
    return {
        'status': 'error',
        'findings': [],
        'recommendations': ['This is a template module - implement actual analysis'],
        'technical_details': {'error': 'Template module not implemented'}
    }