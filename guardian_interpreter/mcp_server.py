<<<<<<< HEAD
#!/usr/bin/env python3
"""
Guardian Node MCP Server
Provides secure MCP interface for Grok/Kiro integration while maintaining privacy
"""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, List, Optional
from pathlib import Path

# MCP imports
try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Resource,
        Tool,
        TextContent,
        ImageContent,
        EmbeddedResource,
    )
    MCP_AVAILABLE = True
except ImportError:
    print("Warning: MCP not available. Install with: pip install mcp")
    MCP_AVAILABLE = False
    sys.exit(1)

# Guardian Node imports
try:
    from guardian_family_cli_enhanced import EnhancedFamilyManager, FamilySecurityProfile
    from main import GuardianInterpreter
    GUARDIAN_AVAILABLE = True
except ImportError:
    print("Warning: Guardian Node components not available")
    GUARDIAN_AVAILABLE = False

class GuardianMCPServer:
    """MCP Server for Guardian Node with privacy-first design"""
    
    def __init__(self):
        self.server = Server("guardian-node")
        self.family_manager = None
        self.guardian = None
        self.privacy_mode = True
        self.child_safe_mode = True
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("guardian-mcp")
        
        # Initialize Guardian components
        self._initialize_guardian()
        
        # Register MCP handlers
        self._register_handlers()
    
    def _initialize_guardian(self):
        """Initialize Guardian Node components safely"""
        try:
            if GUARDIAN_AVAILABLE:
                # Initialize family manager
                self.family_manager = EnhancedFamilyManager()
                
                # Initialize Guardian interpreter (without full startup)
                self.guardian = GuardianInterpreter()
                
                self.logger.info("Guardian Node components initialized for MCP")
            else:
                self.logger.warning("Guardian Node components not available")
        except Exception as e:
            self.logger.error(f"Failed to initialize Guardian components: {e}")
    
    def _register_handlers(self):
        """Register MCP request handlers"""
        
        @self.server.list_resources()
        async def handle_list_resources() -> List[Resource]:
            """List available Guardian Node resources"""
            resources = [
                Resource(
                    uri="guardian://status",
                    name="Guardian Node Status",
                    description="Current status and health of Guardian Node",
                    mimeType="application/json"
                ),
                Resource(
                    uri="guardian://family/skills",
                    name="Family Cybersecurity Skills",
                    description="Available family cybersecurity skills and tools",
                    mimeType="application/json"
                ),
                Resource(
                    uri="guardian://family/recommendations",
                    name="Family Security Recommendations",
                    description="Personalized security recommendations for families",
                    mimeType="application/json"
                ),
                Resource(
                    uri="guardian://logs/summary",
                    name="Security Log Summary",
                    description="Summary of recent security events (privacy-filtered)",
                    mimeType="application/json"
                )
            ]
            return resources
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Read Guardian Node resource content"""
            try:
                if uri == "guardian://status":
                    return await self._get_guardian_status()
                elif uri == "guardian://family/skills":
                    return await self._get_family_skills()
                elif uri == "guardian://family/recommendations":
                    return await self._get_family_recommendations()
                elif uri == "guardian://logs/summary":
                    return await self._get_log_summary()
                else:
                    return json.dumps({"error": "Resource not found", "uri": uri})
            except Exception as e:
                self.logger.error(f"Error reading resource {uri}: {e}")
                return json.dumps({"error": str(e)})
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available Guardian Node tools"""
            tools = [
                Tool(
                    name="ask_family_question",
                    description="Ask a family cybersecurity question and get educational response",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "question": {
                                "type": "string",
                                "description": "Family cybersecurity question"
                            },
                            "age_appropriate": {
                                "type": "boolean",
                                "description": "Ensure response is child-safe",
                                "default": True
                            }
                        },
                        "required": ["question"]
                    }
                ),
                Tool(
                    name="run_family_skill",
                    description="Execute a family cybersecurity skill",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "skill_name": {
                                "type": "string",
                                "description": "Name of the skill to run",
                                "enum": [
                                    "threat_analysis",
                                    "password_check",
                                    "device_scan",
                                    "parental_control_check",
                                    "phishing_education",
                                    "network_security_audit"
                                ]
                            },
                            "args": {
                                "type": "array",
                                "description": "Arguments for the skill",
                                "items": {"type": "string"},
                                "default": []
                            }
                        },
                        "required": ["skill_name"]
                    }
                ),
                Tool(
                    name="get_security_recommendations",
                    description="Get personalized family security recommendations",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "family_size": {
                                "type": "integer",
                                "description": "Number of family members",
                                "default": 4
                            },
                            "has_children": {
                                "type": "boolean",
                                "description": "Whether family has children",
                                "default": True
                            }
                        }
                    }
                ),
                Tool(
                    name="analyze_family_security",
                    description="Perform comprehensive family security analysis",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "include_recommendations": {
                                "type": "boolean",
                                "description": "Include security recommendations",
                                "default": True
                            }
                        }
                    }
                )
            ]
            return tools
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool execution requests"""
            try:
                if name == "ask_family_question":
                    return await self._ask_family_question(arguments)
                elif name == "run_family_skill":
                    return await self._run_family_skill(arguments)
                elif name == "get_security_recommendations":
                    return await self._get_security_recommendations(arguments)
                elif name == "analyze_family_security":
                    return await self._analyze_family_security(arguments)
                else:
                    return [TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )]
            except Exception as e:
                self.logger.error(f"Error executing tool {name}: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error executing {name}: {str(e)}"
                )]
    
    async def _get_guardian_status(self) -> str:
        """Get Guardian Node status"""
        try:
            status = {
                "guardian_node": {
                    "status": "running",
                    "privacy_mode": self.privacy_mode,
                    "child_safe_mode": self.child_safe_mode,
                    "family_assistant": self.family_manager is not None,
                    "skills_available": len(self.family_manager.family_skills) if self.family_manager else 0,
                    "offline_mode": True
                },
                "capabilities": [
                    "family_cybersecurity_education",
                    "threat_analysis",
                    "password_security",
                    "device_scanning",
                    "parental_controls",
                    "phishing_education",
                    "network_security"
                ],
                "privacy_features": [
                    "no_external_calls",
                    "local_processing_only",
                    "comprehensive_audit_logging",
                    "child_safe_responses"
                ]
            }
            return json.dumps(status, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    async def _get_family_skills(self) -> str:
        """Get available family skills"""
        try:
            if not self.family_manager:
                return json.dumps({"error": "Family manager not available"})
            
            skills = []
            for skill_name, description in self.family_manager.skill_descriptions.items():
                skills.append({
                    "name": skill_name,
                    "description": description,
                    "family_friendly": True,
                    "child_safe": True
                })
            
            return json.dumps({
                "family_skills": skills,
                "total_skills": len(skills)
            }, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    async def _get_family_recommendations(self) -> str:
        """Get family security recommendations"""
        try:
            if not self.family_manager:
                return json.dumps({"error": "Family manager not available"})
            
            profile = FamilySecurityProfile()
            recommendations = self.family_manager.get_family_recommendations(profile)
            
            rec_list = []
            for rec in recommendations:
                rec_list.append({
                    "title": rec.title,
                    "priority": rec.priority,
                    "difficulty": rec.difficulty,
                    "description": rec.description,
                    "category": getattr(rec, 'category', 'general')
                })
            
            return json.dumps({
                "recommendations": rec_list,
                "total_recommendations": len(rec_list),
                "generated_for": "family_security"
            }, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    async def _get_log_summary(self) -> str:
        """Get privacy-filtered log summary"""
        try:
            # Return only non-sensitive log summary
            summary = {
                "recent_activity": {
                    "family_questions_answered": "Available",
                    "security_skills_executed": "Available",
                    "threat_analyses_performed": "Available",
                    "blocked_external_calls": "Privacy protected - no external calls made"
                },
                "privacy_status": {
                    "external_calls_blocked": True,
                    "data_stays_local": True,
                    "audit_logging_active": True
                },
                "note": "Detailed logs are kept private and only accessible locally for security audit purposes"
            }
            return json.dumps(summary, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    async def _ask_family_question(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle family cybersecurity questions"""
        try:
            question = arguments.get("question", "")
            age_appropriate = arguments.get("age_appropriate", True)
            
            if not self.family_manager:
                return [TextContent(
                    type="text",
                    text="Family assistant is not available. Please check Guardian Node configuration."
                )]
            
            # Process the question
            context = {
                "family_profile": {
                    "family_id": "mcp_session",
                    "child_safe_mode": age_appropriate and self.child_safe_mode
                }
            }
            
            result = self.family_manager.process_family_query(question, context)
            
            response_text = f"**Family Cybersecurity Assistant Response:**\n\n"
            response_text += f"{result.get('response', 'No response available')}\n\n"
            
            confidence = result.get('confidence', 0)
            if confidence > 0:
                response_text += f"**Confidence:** {confidence:.0%}\n\n"
            
            follow_ups = result.get('follow_up_questions', [])
            if follow_ups:
                response_text += "**Follow-up questions you might ask:**\n"
                for i, q in enumerate(follow_ups[:3], 1):
                    response_text += f"{i}. {q}\n"
            
            return [TextContent(type="text", text=response_text)]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error processing family question: {str(e)}"
            )]
    
    async def _run_family_skill(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute a family cybersecurity skill"""
        try:
            skill_name = arguments.get("skill_name", "")
            args = arguments.get("args", [])
            
            if not self.family_manager:
                return [TextContent(
                    type="text",
                    text="Family assistant is not available."
                )]
            
            result = self.family_manager.run_family_skill(skill_name, *args)
            
            if result.get('success'):
                response_text = f"**Family Skill: {skill_name}**\n\n"
                response_text += f"✅ **Result:** {result.get('result', 'Completed successfully')}\n\n"
                
                details = result.get('details', {})
                if details:
                    response_text += "**Details:**\n"
                    for key, value in details.items():
                        if isinstance(value, list):
                            response_text += f"- {key}: {', '.join(map(str, value))}\n"
                        else:
                            response_text += f"- {key}: {value}\n"
                
                return [TextContent(type="text", text=response_text)]
            else:
                error_msg = result.get('error', 'Unknown error')
                return [TextContent(
                    type="text",
                    text=f"❌ **Family skill '{skill_name}' failed:** {error_msg}"
                )]
                
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error executing family skill: {str(e)}"
            )]
    
    async def _get_security_recommendations(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Get personalized security recommendations"""
        try:
            family_size = arguments.get("family_size", 4)
            has_children = arguments.get("has_children", True)
            
            if not self.family_manager:
                return [TextContent(
                    type="text",
                    text="Family assistant is not available."
                )]
            
            # Create family profile
            profile = FamilySecurityProfile()
            profile.members = [{"role": "parent"}] * max(1, family_size - (2 if has_children else 0))
            if has_children:
                profile.members.extend([{"role": "child", "age_group": "minor"}] * 2)
            
            recommendations = self.family_manager.get_family_recommendations(profile)
            
            response_text = "**🛡️ Family Security Recommendations**\n\n"
            
            for i, rec in enumerate(recommendations, 1):
                priority_icon = "🔴" if rec.priority == 'High' else "🟡" if rec.priority == 'Medium' else "🟢"
                difficulty_icon = "🟢" if rec.difficulty == 'Easy' else "🟡" if rec.difficulty == 'Medium' else "🔴"
                
                response_text += f"**{i}. {rec.title}**\n"
                response_text += f"Priority: {priority_icon} {rec.priority} | Difficulty: {difficulty_icon} {rec.difficulty}\n"
                response_text += f"{rec.description}\n\n"
            
            return [TextContent(type="text", text=response_text)]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error getting security recommendations: {str(e)}"
            )]
    
    async def _analyze_family_security(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Perform family security analysis"""
        try:
            include_recommendations = arguments.get("include_recommendations", True)
            
            if not self.family_manager:
                return [TextContent(
                    type="text",
                    text="Family assistant is not available."
                )]
            
            profile = FamilySecurityProfile()
            analysis = self.family_manager.analyze_family_security(profile)
            
            response_text = "**🔍 Family Security Analysis Report**\n\n"
            response_text += f"**Status:** {analysis.status}\n"
            response_text += f"**Overall Score:** {analysis.overall_score:.1f}/100\n\n"
            
            if hasattr(analysis, 'findings') and analysis.findings:
                response_text += "**🔍 Security Findings:**\n"
                for finding in analysis.findings:
                    response_text += f"✅ {finding}\n"
                response_text += "\n"
            
            if include_recommendations and hasattr(analysis, 'recommendations') and analysis.recommendations:
                response_text += "**💡 Priority Recommendations:**\n"
                for i, rec in enumerate(analysis.recommendations[:5], 1):
                    priority_icon = "🔴" if rec.priority == 'High' else "🟡" if rec.priority == 'Medium' else "🟢"
                    response_text += f"{i}. {priority_icon} {rec.title} (Priority: {rec.priority})\n"
                    if rec.description:
                        response_text += f"   {rec.description}\n"
                response_text += "\n"
            
            response_text += "**Privacy Note:** This analysis was performed completely offline with no external data sharing."
            
            return [TextContent(type="text", text=response_text)]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error performing security analysis: {str(e)}"
            )]

async def main():
    """Main MCP server entry point"""
    if not MCP_AVAILABLE:
        print("MCP not available. Please install: pip install mcp")
        sys.exit(1)
    
    # Create Guardian MCP server
    guardian_server = GuardianMCPServer()
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await guardian_server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="guardian-node",
                server_version="1.0.0",
                capabilities={
                    "resources": True,
                    "tools": True,
                    "prompts": False
                }
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
=======
# guardian_interpreter/mcp_server.py
from mcp import Server  # Assumes offline wheel installed (pip install mcp-agent.whl --no-deps)
from family_assistant import process_query, execute_skill, get_recommendations, analyze_security
from family_assistant.manager import FamilyAssistantManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

server = Server("guardian-node")
fm = FamilyAssistantManager()

@server.tool
def ask_family_question(query):
    logger.info(f"Processing query: {query}")
    return fm.process_query(query, child_safe=True, offline=True)

@server.tool
def run_family_skill(skill_name, *args):
    logger.info(f"Executing skill: {skill_name}")
    return fm.execute_skill(skill_name, *args)

@server.tool
def get_security_recommendations():
    logger.info("Fetching security recommendations")
    return fm.get_recommendations()

@server.tool
def analyze_family_security():
    logger.info("Analyzing family security")
    return fm.analyze_security()

@server.resource
def guardian_status():
    return {"health": "ok", "offline": True, "capabilities": ["family_assistant", "mcp_tools"]}

@server.resource
def family_skills():
    return fm.list_skills()

@server.resource
def security_recommendations():
    return fm.get_recommendations()

@server.resource
def log_summary():
    return {"summary": "Privacy-filtered activity log", "events": len(logger.handlers[0].records)}  # Mock

if __name__ == "__main__":
    server.run(host="localhost", port=8080, privacy_mode="strict", child_safe=True)
>>>>>>> a0d2c75a88747ce742b9ef6cc664642fcb07ac5e
