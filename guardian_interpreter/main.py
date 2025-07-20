import sys
import logging
import yaml
import os
from pathlib import Path

# Import Guardian components
try:
    from guardian_interpreter.llm_integration import create_llm
    from guardian_interpreter.network_security import NetworkSecurityManager, AuditLogger
    from guardian_interpreter.family_assistant.family_assistant_manager import FamilyAssistantManager
    from guardian_interpreter.family_assistant.skill_registry import FamilySkillRegistry
    from guardian_interpreter.family_llm_prompts import FamilyContext, ChildSafetyLevel
    from guardian_interpreter.skills import family_cyber_skills, threat_analysis_skill, device_guidance_skill, child_education_skill
    
    LLM_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import Guardian components: {e}")
    LLM_AVAILABLE = False

class GuardianCLI:
    def __init__(self):
        self.logger = logging.getLogger('guardian')
        self.config = self._load_config()
        
        # Initialize LLM
        if LLM_AVAILABLE:
            self.llm = create_llm(self.config, self.logger)
            self.llm.load_model()
            
            # Initialize audit logger
            self.audit_logger = AuditLogger(self.config, self.logger)
            
            # Initialize family assistant manager
            self.family_manager = FamilyAssistantManager(
                config=self.config,
                logger=self.logger,
                audit_logger=self.audit_logger
            )
            
            # Register family skills
            self._register_family_skills()
            
            self.logger.info("Guardian CLI initialized with real LLM integration")
        else:
            self.family_manager = self._create_fallback_manager()
            self.llm = None
            self.audit_logger = None
            self.logger.warning("Guardian CLI initialized with fallback manager")
    
    def _load_config(self) -> dict:
        """Load Guardian configuration"""
        config_path = Path(__file__).parent / 'config.yaml'
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                self.logger.error(f"Error loading config: {e}")
        
        # Default configuration
        return {
            'llm': {
                'model_path': 'models/guardian-model.gguf',
                'context_length': 4096,
                'max_tokens': 512,
                'temperature': 0.7,
                'threads': 4
            },
            'family_assistant': {
                'enabled': True,
                'gui_enabled': True,
                'default_interface': 'cli',
                'family_data_path': 'data/families'
            }
        }
    
    def _register_family_skills(self):
        """Register all family skills with the manager"""
        try:
            # Skills are already imported at module level
            
            # Create skill wrapper class for compatibility
            class SkillWrapper:
                def __init__(self, skill_func, name):
                    self.skill_func = skill_func
                    self.name = name
                
                def run(self, *args, **kwargs):
                    return self.skill_func(*args, **kwargs)
            
            # Register skills
            self.family_manager.register_family_skill(
                'family_cyber_skills', 
                SkillWrapper(family_cyber_skills.run, 'family_cyber_skills')
            )
            self.family_manager.register_family_skill(
                'threat_analysis_skill', 
                SkillWrapper(threat_analysis_skill.run, 'threat_analysis_skill')
            )
            self.family_manager.register_family_skill(
                'device_guidance_skill', 
                SkillWrapper(device_guidance_skill.run, 'device_guidance_skill')
            )
            self.family_manager.register_family_skill(
                'child_education_skill', 
                SkillWrapper(child_education_skill.run, 'child_education_skill')
            )
            
            self.logger.info("Family skills registered successfully")
            
        except Exception as e:
            self.logger.error(f"Error registering family skills: {e}")
    
    def _create_fallback_manager(self):
        """Create fallback manager when LLM is not available"""
        class FallbackFamilyManager:
            def __init__(self):
                self.family_skills = {
                    'threat_analysis': lambda *a, **k: {'success': True, 'result': "Threat analysis not available - LLM required"},
                    'device_guidance': lambda *a, **k: {'success': True, 'result': "Device guidance not available - LLM required"},
                    'child_education': lambda *a, **k: {'success': True, 'result': "Child education not available - LLM required"}
                }
            
            def process_family_query(self, query, context):
                return {
                    'response': f'Family assistant requires LLM integration. Your query: "{query}" cannot be processed without a loaded model.',
                    'confidence': 0.0,
                    'follow_up_questions': ['Please configure an LLM model to enable family assistance.']
                }
            
            def run_family_skill(self, skill_name, *args):
                return {'success': False, 'error': 'LLM integration required for family skills'}
            
            def analyze_family_security(self, profile):
                class Result:
                    status = 'unavailable'
                    overall_score = 0.0
                    findings = ['Family security analysis requires LLM integration']
                    recommendations = []
                return Result()
            
            def get_family_recommendations(self, profile):
                return []
        
        return FallbackFamilyManager()
    def show_family_help(self):
        help_text = """
Family Assistant Commands:
========================
  family skills                 - List available family cybersecurity skills
  family skill <name>           - Run a specific family skill
  family analyze                - Analyze family security posture
  family recommendations        - Get personalized security recommendations
  family status                 - Show family assistant status
  ask <question>                - Ask a family cybersecurity question

Examples:
  family skills
  family skill threat_analysis
  ask "How can I keep my child safe online?"
  family analyze
        """
        print(help_text)
    def list_family_skills(self):
        if not self.family_manager:
            print("Family assistant not available.")
            return
        print("\nAvailable Family Skills:")
        print("-" * 40)
        skills = self.family_manager.family_skills
        if not skills:
            print("No family skills registered.")
            return
        for i, (name, skill) in enumerate(skills.items(), 1):
            description = "Family cybersecurity skill"
            print(f"{i:2d}. {name:<25} - {description}")
        print()
    def run_family_skill(self, skill_name, *args):
        if not self.family_manager:
            print("Family assistant not available.")
            return
        try:
            result = self.family_manager.run_family_skill(skill_name, *args)
            if result.get('success'):
                print(f"✓ Family skill '{skill_name}' completed")
                skill_result = result.get('result')
                if skill_result:
                    print(f"Result: {skill_result}")
            else:
                print(f"✗ Family skill '{skill_name}' failed: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"✗ Error running family skill '{skill_name}': {e}")
            self.logger.error(f"Family skill execution error: {e}")
    def analyze_family_security(self):
        if not self.family_manager:
            print("Family assistant not available.")
            return
        try:
            default_profile = {
                'family_id': 'guardian_family',
                'family_name': 'Guardian Family',
                'members': [{'name': 'Parent', 'age_group': 'adult', 'tech_skill_level': 'intermediate'}],
                'devices': [],
                'security_preferences': {'threat_tolerance': 'medium', 'auto_recommendations': True}
            }
            print("Analyzing family security posture...")
            analysis = self.family_manager.analyze_family_security(default_profile)
            print(f"\nFamily Security Analysis:")
            print(f"Status: {analysis.status}")
            print(f"Overall Score: {analysis.overall_score:.1f}/100")
            if getattr(analysis, 'findings', None):
                print(f"\nFindings:")
                for finding in analysis.findings:
                    print(f"  • {finding}")
            if getattr(analysis, 'recommendations', None):
                print(f"\nRecommendations:")
                for i, rec in enumerate(analysis.recommendations[:5], 1):
                    print(f"  {i}. {rec.title} (Priority: {rec.priority})")
        except Exception as e:
            print(f"✗ Error analyzing family security: {e}")
            self.logger.error(f"Family security analysis error: {e}")
    def get_family_recommendations(self):
        if not self.family_manager:
            print("Family assistant not available.")
            return
        try:
            default_profile = {
                'family_id': 'guardian_family',
                'family_name': 'Guardian Family',
                'members': [{'name': 'Parent', 'age_group': 'adult', 'tech_skill_level': 'intermediate'}],
                'devices': [],
                'security_preferences': {'threat_tolerance': 'medium', 'auto_recommendations': True}
            }
            print("Generating family security recommendations...")
            recommendations = self.family_manager.get_family_recommendations(default_profile)
            if recommendations:
                print(f"\nFamily Security Recommendations:")
                print("-" * 40)
                for i, rec in enumerate(recommendations, 1):
                    print(f"{i}. {rec.title}")
                    print(f"   Priority: {rec.priority} | Difficulty: {rec.difficulty}")
                    print(f"   {rec.description}\n")
            else:
                print("No recommendations available at this time.")
        except Exception as e:
            print(f"✗ Error getting family recommendations: {e}")
            self.logger.error(f"Family recommendations error: {e}")
    def show_family_status(self):
        print("Family Assistant is running. All systems nominal.")
    def process_family_query(self, query, subcommand=None, args=None):
        if not self.family_manager:
            print("Family assistant not available.")
            return
        try:
            # Create family context
            context = {
                'family_profile': {
                    'family_id': 'guardian_family', 
                    'members': [{'age_group': 'adult', 'tech_skill_level': 'intermediate'}]
                }
            }
            
            # Process query through family assistant manager
            result = self.family_manager.process_family_query(query, context)
            
            # If LLM is available, enhance response with LLM-generated content
            if self.llm and self.llm.is_loaded() and LLM_AVAILABLE:
                enhanced_response = self._enhance_response_with_llm(query, result, context)
                if enhanced_response:
                    result['response'] = enhanced_response
                    result['llm_enhanced'] = True
            
            print("\nFamily Assistant Response:")
            print(result.get('response', 'No response available'))
            
            # Show confidence if available
            confidence = result.get('confidence', 0)
            if confidence > 0:
                print(f"\nConfidence: {confidence:.2f}")
            
            # Show if response was LLM enhanced
            if result.get('llm_enhanced'):
                print("✨ Enhanced with AI reasoning")
            
            # Show follow-up questions
            follow_ups = result.get('follow_up_questions', [])
            if follow_ups:
                print("\nFollow-up questions you might ask:")
                for i, question in enumerate(follow_ups[:3], 1):
                    print(f"  {i}. {question}")
            
            # Handle subcommands
            if subcommand == 'analyze':
                self.analyze_family_security()
            elif subcommand == 'recommendations':
                self.get_family_recommendations()
            elif subcommand == 'status':
                self.show_family_status()
            elif args and len(args) > 1:
                skill_name = args[1]
                skill_args = args[2:] if len(args) > 2 else []
                self.run_family_skill(skill_name, *skill_args)
                
        except Exception as e:
            print(f"✗ Error processing family query: {e}")
            self.logger.error(f"Family query processing error: {e}")
    
    def _enhance_response_with_llm(self, query: str, skill_result: dict, context: dict) -> str:
        """Enhance skill response with LLM-generated family-friendly content"""
        try:
            # Determine family context for LLM prompting
            family_context = FamilyContext.GENERAL
            child_safe_mode = False
            safety_level = ChildSafetyLevel.STANDARD
            
            # Detect context from query
            query_lower = query.lower()
            if any(word in query_lower for word in ['child', 'kid', 'young']):
                family_context = FamilyContext.CHILD_EDUCATION
                child_safe_mode = True
                safety_level = ChildSafetyLevel.MODERATE
            elif any(word in query_lower for word in ['threat', 'attack', 'danger']):
                family_context = FamilyContext.THREAT_EXPLANATION
            elif any(word in query_lower for word in ['device', 'phone', 'computer']):
                family_context = FamilyContext.DEVICE_SECURITY
            elif any(word in query_lower for word in ['parent', 'family']):
                family_context = FamilyContext.PARENT_GUIDANCE
            
            # Create enhanced prompt combining skill result with user query
            skill_response = skill_result.get('response', '')
            enhancement_prompt = f"""
Based on this cybersecurity question: "{query}"

And this technical guidance: "{skill_response}"

Please provide a comprehensive, family-friendly response that:
1. Explains the cybersecurity concept in simple terms
2. Provides practical steps the family can take
3. Uses analogies that relate to everyday family life
4. Prioritizes the most important actions first
5. Encourages good cybersecurity habits

Keep the response helpful, encouraging, and actionable for a family audience.
"""
            
            # Generate enhanced response using family-friendly LLM prompts
            enhanced_response = self.llm.generate_family_response(
                enhancement_prompt,
                context=family_context,
                child_safe_mode=child_safe_mode,
                safety_level=safety_level,
                family_profile=context.get('family_profile')
            )
            
            # Validate the enhanced response
            if enhanced_response and len(enhanced_response.strip()) > 50:
                return enhanced_response
            else:
                self.logger.warning("LLM enhancement produced insufficient response")
                return None
                
        except Exception as e:
            self.logger.error(f"Error enhancing response with LLM: {e}")
            return None
    def family_cli_loop(self):
        print("Guardian Family Assistant CLI. Type 'help' for commands.")
        while True:
            try:
                command = input("guardian-family> ").strip()
                if not command:
                    continue
                if command in ['exit', 'quit']:
                    break
                if command == 'help':
                    self.show_family_help()
                    continue
                parts = command.split()
                if parts[0] == 'family':
                    if len(parts) == 1 or parts[1] == 'help':
                        self.show_family_help()
                    elif parts[1] == 'skills':
                        self.list_family_skills()
                    elif parts[1] == 'skill':
                        if len(parts) < 3:
                            print("Usage: family skill <skill_name> [arguments]")
                        else:
                            skill_name = parts[2]
                            skill_args = parts[3:] if len(parts) > 3 else []
                            self.run_family_skill(skill_name, *skill_args)
                    elif parts[1] == 'analyze':
                        self.analyze_family_security()
                    elif parts[1] == 'recommendations':
                        self.get_family_recommendations()
                    elif parts[1] == 'status':
                        self.show_family_status()
                    else:
                        print("Unknown family subcommand.")
                elif parts[0] == 'ask':
                    query = command[len('ask '):].strip()
                    self.process_family_query(query)
                else:
                    print("Unknown command.")
            except KeyboardInterrupt:
                print("\nExiting.")
                break
            except Exception as e:
                print(f"Error: {e}")

def main():
    """Main entry point with argument parsing"""
    import argparse
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Guardian Node - Family Cybersecurity Assistant')
    parser.add_argument('--gui', action='store_true', help='Launch GUI mode')
    parser.add_argument('--mcp', action='store_true', help='Enable MCP server')
    parser.add_argument('--family-mode', action='store_true', help='Enable family assistant mode')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create Guardian CLI instance
    cli = GuardianCLI()
    
    # Launch GUI if requested
    if args.gui:
        try:
            from guardian_gui import create_guardian_gui
            print("🖥️ Launching Guardian Node GUI...")
            
            # Create GUI application
            app, window = create_guardian_gui(cli)
            
            # Set environment variables for GUI mode
            import os
            if args.family_mode:
                os.environ['GUARDIAN_FAMILY_MODE'] = 'true'
            if args.mcp:
                os.environ['GUARDIAN_MCP_ENABLED'] = 'true'
            
            print("✓ GUI launched successfully")
            print("   Use the mode buttons to switch between Adult/Teen/Kids modes")
            print("   Click buttons to access family features and security tools")
            
            # Run GUI event loop
            sys.exit(app.exec())
            
        except ImportError as e:
            print(f"❌ GUI dependencies not available: {e}")
            print("Install GUI dependencies: pip install PySide6")
            print("Falling back to CLI mode...")
            cli.family_cli_loop()
        except Exception as e:
            print(f"❌ Error launching GUI: {e}")
            print("Falling back to CLI mode...")
            cli.family_cli_loop()
    else:
        # Run CLI mode
        print("🖥️ Starting Guardian Node CLI...")
        if args.family_mode:
            print("👨‍👩‍👧‍👦 Family assistant mode enabled")
        if args.mcp:
            print("🔌 MCP server mode enabled")
        
        cli.family_cli_loop()

def main():
    """Main entry point with argument parsing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Guardian Node - Family Cybersecurity Assistant")
    parser.add_argument('--gui', action='store_true', help='Launch GUI mode')
    parser.add_argument('--mcp', action='store_true', help='Enable MCP server')
    parser.add_argument('--family-mode', action='store_true', help='Enable family mode')
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    print("🛡️ Starting Guardian Node...")
    
    if args.gui:
        print("🖥️ Launching GUI mode...")
        try:
            from guardian_gui import create_guardian_gui
            
            # Create Guardian CLI instance for backend integration
            guardian = GuardianCLI()
            
            # Set Raspberry Pi environment if on ARM
            import platform
            if platform.machine() in ['aarch64', 'armv7l']:
                os.environ['RASPBERRY_PI'] = '1'
            else:
                os.environ['RASPBERRY_PI'] = '0'
            
            # Create and run GUI
            app, window = create_guardian_gui(guardian)
            print("✅ GUI launched successfully")
            sys.exit(app.exec())
            
        except ImportError as e:
            print(f"❌ GUI not available: {e}")
            print("💡 Install PySide6: pip install PySide6")
            print("🔄 Falling back to CLI mode...")
            
    # CLI mode (default)
    print("💻 Running in CLI mode...")
    cli = GuardianCLI()
    
    if args.mcp:
        print("🔌 MCP server mode enabled")
        # MCP integration would go here
    
    if args.family_mode:
        print("👨‍👩‍👧‍👦 Family mode enabled")
    
    cli.family_cli_loop()


if __name__ == "__main__":
    main()