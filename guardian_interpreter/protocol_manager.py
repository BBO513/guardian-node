"""
Protocol Manager Framework for Guardian Interpreter
Extends existing Guardian architecture with modular protocol analysis capabilities
Provides family-friendly protocol analysis reporting
"""

import os
import sys
import logging
import importlib.util
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
import threading
import time

@dataclass
class ProtocolAnalysisResult:
    """Result of a protocol analysis"""
    protocol_name: str
    status: str  # "secure", "warning", "critical", "error"
    findings: List[Dict[str, Any]]
    recommendations: List[str]
    family_friendly_summary: str
    technical_details: Dict[str, Any]
    timestamp: datetime
    execution_time: float

@dataclass
class ProtocolModule:
    """Protocol module metadata"""
    name: str
    description: str
    version: str
    author: str
    family_friendly: bool
    supported_protocols: List[str]
    module_path: str
    loaded_module: Any = None

class ProtocolManager:
    """
    Protocol Manager that extends existing Guardian architecture
    Manages protocol module loading, execution, and family-friendly reporting
    """
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger, audit_logger=None):
        self.config = config
        self.logger = logger
        self.audit_logger = audit_logger
        self.protocol_config = config.get('protocol_modules', {})
        
        # Protocol modules storage
        self.protocol_modules: Dict[str, ProtocolModule] = {}
        self.analysis_results: List[ProtocolAnalysisResult] = []
        self.analysis_lock = threading.Lock()
        
        # Family-friendly formatting
        self.family_mode = self.protocol_config.get('family_friendly_mode', True)
        
        # Initialize protocol manager
        self._setup_protocol_manager()
    
    def _setup_protocol_manager(self):
        """Setup protocol manager and logging"""
        self.logger.info("Protocol Manager initializing...")
        
        # Create protocols directory if it doesn't exist
        protocols_dir = self.protocol_config.get('modules_directory', 'protocols')
        os.makedirs(protocols_dir, exist_ok=True)
        
        self.logger.info(f"Protocol modules directory: {protocols_dir}")
        self.logger.info(f"Family-friendly mode: {self.family_mode}")
        
        if self.audit_logger:
            self.audit_logger.log_system_event("Protocol Manager initialized", {
                'modules_directory': protocols_dir,
                'family_friendly_mode': self.family_mode
            })
    
    def load_protocol_modules(self) -> int:
        """
        Load all protocol modules from the protocols directory
        
        Returns:
            int: Number of modules loaded successfully
        """
        if not self.protocol_config.get('enabled', True):
            self.logger.info("Protocol modules disabled in configuration")
            return 0
        
        protocols_dir = self.protocol_config.get('modules_directory', 'protocols')
        protocols_path = Path(protocols_dir)
        
        if not protocols_path.exists():
            self.logger.warning(f"Protocol modules directory {protocols_dir} not found")
            return 0
        
        loaded_count = 0
        for protocol_file in protocols_path.glob('*.py'):
            if protocol_file.name.startswith('__'):
                continue  # Skip __init__.py and similar files
            
            try:
                module_name = protocol_file.stem
                loaded_module = self._load_protocol_module(protocol_file, module_name)
                
                if loaded_module:
                    # Get module metadata
                    metadata = self._extract_module_metadata(loaded_module, module_name, str(protocol_file))
                    self.protocol_modules[module_name] = metadata
                    loaded_count += 1
                    
                    self.logger.info(f"Loaded protocol module: {module_name}")
                    
                    if self.audit_logger:
                        self.audit_logger.log_system_event(f"Protocol module loaded", {
                            'module': module_name,
                            'version': metadata.version,
                            'family_friendly': metadata.family_friendly
                        })
                    
            except Exception as e:
                self.logger.error(f"Failed to load protocol module {protocol_file}: {e}")
                self.logger.debug(traceback.format_exc())
        
        self.logger.info(f"Protocol modules loading complete: {loaded_count} modules loaded")
        return loaded_count
    
    def _load_protocol_module(self, module_path: Path, module_name: str) -> Optional[Any]:
        """Load a single protocol module"""
        try:
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Validate required functions
            required_functions = ['analyze', 'get_metadata']
            for func_name in required_functions:
                if not hasattr(module, func_name):
                    self.logger.error(f"Protocol module {module_name} missing required function: {func_name}")
                    return None
            
            return module
            
        except Exception as e:
            self.logger.error(f"Error loading protocol module {module_name}: {e}")
            return None
    
    def _extract_module_metadata(self, module: Any, module_name: str, module_path: str) -> ProtocolModule:
        """Extract metadata from a loaded protocol module"""
        try:
            metadata_func = getattr(module, 'get_metadata')
            metadata = metadata_func()
            
            return ProtocolModule(
                name=metadata.get('name', module_name),
                description=metadata.get('description', 'No description available'),
                version=metadata.get('version', '1.0.0'),
                author=metadata.get('author', 'Unknown'),
                family_friendly=metadata.get('family_friendly', True),
                supported_protocols=metadata.get('supported_protocols', []),
                module_path=module_path,
                loaded_module=module
            )
            
        except Exception as e:
            self.logger.error(f"Error extracting metadata from {module_name}: {e}")
            # Return default metadata
            return ProtocolModule(
                name=module_name,
                description='No description available',
                version='1.0.0',
                author='Unknown',
                family_friendly=True,
                supported_protocols=[],
                module_path=module_path,
                loaded_module=module
            )
    
    def list_protocol_modules(self) -> List[Dict[str, Any]]:
        """List all loaded protocol modules"""
        modules_info = []
        for name, module in self.protocol_modules.items():
            modules_info.append({
                'name': module.name,
                'description': module.description,
                'version': module.version,
                'author': module.author,
                'family_friendly': module.family_friendly,
                'supported_protocols': module.supported_protocols
            })
        return modules_info
    
    def run_protocol_analysis(self, module_name: str, target: str = None, **kwargs) -> Optional[ProtocolAnalysisResult]:
        """
        Run protocol analysis using specified module
        
        Args:
            module_name: Name of the protocol module to use
            target: Target for analysis (IP, network, etc.)
            **kwargs: Additional arguments for the protocol module
            
        Returns:
            ProtocolAnalysisResult or None if failed
        """
        if module_name not in self.protocol_modules:
            self.logger.error(f"Protocol module '{module_name}' not found")
            return None
        
        module_info = self.protocol_modules[module_name]
        module = module_info.loaded_module
        
        start_time = time.time()
        
        try:
            self.logger.info(f"Running protocol analysis: {module_name} on target: {target}")
            
            if self.audit_logger:
                self.audit_logger.log_system_event(f"Protocol analysis started", {
                    'module': module_name,
                    'target': target,
                    'kwargs': kwargs
                })
            
            # Run the analysis
            analysis_func = getattr(module, 'analyze')
            raw_result = analysis_func(target=target, **kwargs)
            
            execution_time = time.time() - start_time
            
            # Process and format the result
            result = self._process_analysis_result(
                module_name, raw_result, execution_time
            )
            
            # Store the result
            with self.analysis_lock:
                self.analysis_results.append(result)
                # Keep only recent results (last 1000)
                if len(self.analysis_results) > 1000:
                    self.analysis_results = self.analysis_results[-1000:]
            
            self.logger.info(f"Protocol analysis completed: {module_name} - Status: {result.status}")
            
            if self.audit_logger:
                self.audit_logger.log_system_event(f"Protocol analysis completed", {
                    'module': module_name,
                    'status': result.status,
                    'findings_count': len(result.findings),
                    'execution_time': execution_time
                })
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Error running protocol analysis {module_name}: {e}"
            self.logger.error(error_msg)
            self.logger.debug(traceback.format_exc())
            
            if self.audit_logger:
                self.audit_logger.log_security_event(f"Protocol analysis error", {
                    'module': module_name,
                    'error': str(e),
                    'execution_time': execution_time
                })
            
            # Return error result
            return ProtocolAnalysisResult(
                protocol_name=module_name,
                status="error",
                findings=[],
                recommendations=[f"Analysis failed: {str(e)}"],
                family_friendly_summary=f"Unable to complete {module_name} analysis due to an error.",
                technical_details={'error': str(e)},
                timestamp=datetime.now(),
                execution_time=execution_time
            )
    
    def _process_analysis_result(self, module_name: str, raw_result: Dict[str, Any], execution_time: float) -> ProtocolAnalysisResult:
        """Process raw analysis result into standardized format"""
        
        # Extract basic information
        status = raw_result.get('status', 'unknown')
        findings = raw_result.get('findings', [])
        recommendations = raw_result.get('recommendations', [])
        technical_details = raw_result.get('technical_details', {})
        
        # Generate family-friendly summary
        family_summary = self._generate_family_friendly_summary(
            module_name, status, findings, recommendations
        )
        
        return ProtocolAnalysisResult(
            protocol_name=module_name,
            status=status,
            findings=findings,
            recommendations=recommendations,
            family_friendly_summary=family_summary,
            technical_details=technical_details,
            timestamp=datetime.now(),
            execution_time=execution_time
        )
    
    def _generate_family_friendly_summary(self, module_name: str, status: str, findings: List[Dict], recommendations: List[str]) -> str:
        """Generate family-friendly summary of analysis results"""
        
        if not self.family_mode:
            return f"Protocol analysis '{module_name}' completed with status: {status}"
        
        # Status-based summaries
        status_messages = {
            'secure': f"✅ Great news! Your {module_name} security looks good.",
            'warning': f"⚠️ We found some areas where your {module_name} security could be improved.",
            'critical': f"🚨 Important: We found some serious security issues with {module_name} that need attention.",
            'error': f"❌ We couldn't complete the {module_name} security check due to a technical issue."
        }
        
        base_message = status_messages.get(status, f"We completed the {module_name} security analysis.")
        
        # Add findings summary
        if findings:
            findings_count = len(findings)
            if findings_count == 1:
                base_message += f" We found 1 item to review."
            else:
                base_message += f" We found {findings_count} items to review."
        
        # Add recommendations summary
        if recommendations:
            rec_count = len(recommendations)
            if rec_count == 1:
                base_message += f" We have 1 recommendation to help improve your security."
            else:
                base_message += f" We have {rec_count} recommendations to help improve your security."
        
        return base_message
    
    def get_analysis_results(self, module_name: str = None, limit: int = 50) -> List[ProtocolAnalysisResult]:
        """Get recent analysis results"""
        with self.analysis_lock:
            results = self.analysis_results
            
            if module_name:
                results = [r for r in results if r.protocol_name == module_name]
            
            return results[-limit:] if results else []
    
    def get_protocol_summary(self) -> Dict[str, Any]:
        """Get summary of protocol manager status"""
        with self.analysis_lock:
            recent_results = self.analysis_results[-10:] if self.analysis_results else []
            
            # Count results by status
            status_counts = {}
            for result in self.analysis_results:
                status = result.status
                status_counts[status] = status_counts.get(status, 0) + 1
            
            return {
                'modules_loaded': len(self.protocol_modules),
                'total_analyses': len(self.analysis_results),
                'status_breakdown': status_counts,
                'recent_results': [
                    {
                        'protocol': r.protocol_name,
                        'status': r.status,
                        'timestamp': r.timestamp.isoformat(),
                        'summary': r.family_friendly_summary
                    }
                    for r in recent_results
                ],
                'family_friendly_mode': self.family_mode
            }
    
    def format_analysis_report(self, result: ProtocolAnalysisResult, detailed: bool = False) -> str:
        """Format analysis result for display"""
        
        if self.family_mode:
            return self._format_family_friendly_report(result, detailed)
        else:
            return self._format_technical_report(result, detailed)
    
    def _format_family_friendly_report(self, result: ProtocolAnalysisResult, detailed: bool) -> str:
        """Format family-friendly analysis report"""
        
        report = []
        report.append(f"🔍 {result.protocol_name.title()} Security Check")
        report.append("=" * 40)
        report.append(f"Status: {result.status.upper()}")
        report.append(f"Completed: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        report.append("Summary:")
        report.append(result.family_friendly_summary)
        report.append("")
        
        if result.recommendations:
            report.append("🛠️ What You Can Do:")
            for i, rec in enumerate(result.recommendations, 1):
                report.append(f"  {i}. {rec}")
            report.append("")
        
        if detailed and result.findings:
            report.append("📋 Detailed Findings:")
            for i, finding in enumerate(result.findings, 1):
                severity = finding.get('severity', 'info')
                description = finding.get('description', 'No description')
                report.append(f"  {i}. [{severity.upper()}] {description}")
            report.append("")
        
        return "\n".join(report)
    
    def _format_technical_report(self, result: ProtocolAnalysisResult, detailed: bool) -> str:
        """Format technical analysis report"""
        
        report = []
        report.append(f"Protocol Analysis Report: {result.protocol_name}")
        report.append("=" * 50)
        report.append(f"Status: {result.status}")
        report.append(f"Execution Time: {result.execution_time:.2f}s")
        report.append(f"Timestamp: {result.timestamp.isoformat()}")
        report.append("")
        
        if result.findings:
            report.append("Findings:")
            for finding in result.findings:
                report.append(f"  - {finding}")
            report.append("")
        
        if result.recommendations:
            report.append("Recommendations:")
            for rec in result.recommendations:
                report.append(f"  - {rec}")
            report.append("")
        
        if detailed and result.technical_details:
            report.append("Technical Details:")
            for key, value in result.technical_details.items():
                report.append(f"  {key}: {value}")
            report.append("")
        
        return "\n".join(report)
    
    def enable_family_mode(self):
        """Enable family-friendly mode"""
        self.family_mode = True
        self.logger.info("Family-friendly mode enabled")
        
        if self.audit_logger:
            self.audit_logger.log_system_event("Family mode enabled")
    
    def disable_family_mode(self):
        """Disable family-friendly mode"""
        self.family_mode = False
        self.logger.info("Family-friendly mode disabled")
        
        if self.audit_logger:
            self.audit_logger.log_system_event("Family mode disabled")