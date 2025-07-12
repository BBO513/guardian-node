#!/usr/bin/env python3
"""
Guardian Interpreter - Local Modular AI Agent (Nodie Edition)
Owner: Blackbox Matrix
Status: Foundation Starter - BOBO

A fully offline, modular AI agent framework for Raspberry Pi 5 (or PC)
- No cloud, no telemetry, no default API calls
- Local LLM via llama-cpp-python and GGUF models
- Modular skill system for protocol modules
- Hard-blocked internet by default
- Full audit logging
"""

import os
import sys
import yaml
import logging
import importlib.util
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import LLM integration
from llm_integration import create_llm
from network_security import NetworkSecurityManager, AuditLogger

class GuardianInterpreter:
    """
    Main Guardian Interpreter class
    Handles configuration, logging, skill loading, and core functionality
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = {}
        self.skills = {}
        self.logger = None
        self.blocked_logger = None
        self.llm = None
        self.network_security = None
        self.audit_logger = None
        self.running = True
        
        # Initialize the Guardian
        self._load_config()
        self._setup_logging()
        self._setup_security_and_audit()
        self._log_startup()
        self._initialize_llm()
        
    def _load_config(self):
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            print(f"✓ Configuration loaded from {self.config_path}")
        except FileNotFoundError:
            print(f"✗ Configuration file {self.config_path} not found!")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"✗ Error parsing configuration: {e}")
            sys.exit(1)
    
    def _setup_logging(self):
        """Setup logging system with privacy-focused audit trail"""
        log_config = self.config.get('logging', {})
        
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Setup main logger
        logging.basicConfig(
            level=getattr(logging, log_config.get('level', 'INFO')),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_config.get('main_log', 'logs/guardian.log')),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('Guardian')
        
        # Setup blocked calls logger
        blocked_handler = logging.FileHandler(log_config.get('blocked_calls_log', 'logs/blocked_calls.log'))
        blocked_handler.setFormatter(logging.Formatter('%(asctime)s - BLOCKED - %(message)s'))
        self.blocked_logger = logging.getLogger('BlockedCalls')
        self.blocked_logger.addHandler(blocked_handler)
        self.blocked_logger.setLevel(logging.INFO)
        
        print("✓ Logging system initialized")
    
    def _setup_security_and_audit(self):
        """Setup network security and audit logging"""
        try:
            # Initialize network security manager
            self.network_security = NetworkSecurityManager(self.config, self.logger, self.blocked_logger)
            
            # Initialize audit logger
            self.audit_logger = AuditLogger(self.config, self.logger)
            
            print("✓ Security and audit systems initialized")
            
        except Exception as e:
            print(f"⚠️  Security setup failed: {e}")
            self.logger.error(f"Security setup error: {e}")
    
    def _log_startup(self):
        """Log Guardian startup information"""
        system_info = self.config.get('system', {})
        self.logger.info("=" * 50)
        self.logger.info(f"Guardian Interpreter Starting")
        self.logger.info(f"Name: {system_info.get('name', 'Guardian Interpreter')}")
        self.logger.info(f"Version: {system_info.get('version', '1.0.0')}")
        self.logger.info(f"Owner: {system_info.get('owner', 'Blackbox Matrix')}")
        self.logger.info(f"Online Mode: {self.config.get('network', {}).get('ALLOW_ONLINE', False)}")
        self.logger.info("=" * 50)
    
    def _initialize_llm(self):
        """Initialize the local LLM"""
        try:
            self.llm = create_llm(self.config, self.logger)
            
            # Try to load the model
            llm_config = self.config.get('llm', {})
            model_path = llm_config.get('model_path', 'models/your-model.gguf')
            
            if os.path.exists(model_path):
                print("Loading LLM model... This may take a moment.")
                if self.llm.load_model():
                    print("✓ LLM model loaded successfully - Nodie is ready!")
                else:
                    print("✗ Failed to load LLM model - Nodie will use fallback responses")
            else:
                print(f"⚠️  LLM model not found at {model_path}")
                print("   Add a GGUF model file to enable full AI functionality")
                
        except Exception as e:
            self.logger.error(f"LLM initialization error: {e}")
            print(f"⚠️  LLM initialization failed: {e}")
    
    def outbound_request(self, url: str, method: str = "GET", **kwargs) -> Optional[Any]:
        """
        Central function for all outbound network requests
        Uses NetworkSecurityManager for enhanced blocking and logging
        """
        if not self.network_security:
            self.logger.error("Network security manager not initialized")
            return None
        
        # Check if request is allowed
        if not self.network_security.is_request_allowed(url, method):
            print(f"🚫 BLOCKED: Outbound request to {url}")
            if self.audit_logger:
                self.audit_logger.log_security_event(f"Blocked outbound request", {
                    'url': url,
                    'method': method
                })
            return None
        
        # If we get here, request is allowed
        print(f"🌐 ALLOWED: Outbound request to {url}")
        if self.audit_logger:
            self.audit_logger.log_security_event(f"Allowed outbound request", {
                'url': url,
                'method': method
            })
        
        # TODO: Implement actual request handling when online is enabled
        # This would use requests library or similar
        return None
    
    def load_skills(self):
        """Load all skills from the skills directory"""
        skills_config = self.config.get('skills', {})
        if not skills_config.get('auto_load', True):
            return
        
        skills_dir = skills_config.get('skills_directory', 'skills')
        skills_path = Path(skills_dir)
        
        if not skills_path.exists():
            self.logger.warning(f"Skills directory {skills_dir} not found")
            return
        
        loaded_count = 0
        for skill_file in skills_path.glob('*.py'):
            if skill_file.name.startswith('__'):
                continue  # Skip __init__.py and similar files
            
            try:
                skill_name = skill_file.stem
                spec = importlib.util.spec_from_file_location(skill_name, skill_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Check if the skill has a 'run' function
                if hasattr(module, 'run'):
                    self.skills[skill_name] = module
                    loaded_count += 1
                    self.logger.info(f"Loaded skill: {skill_name}")
                else:
                    self.logger.warning(f"Skill {skill_name} missing 'run' function")
                    
            except Exception as e:
                self.logger.error(f"Failed to load skill {skill_file}: {e}")
        
        print(f"✓ Loaded {loaded_count} skills")
        self.logger.info(f"Skills loading complete: {loaded_count} skills loaded")
    
    def list_skills(self):
        """List all available skills"""
        if not self.skills:
            print("No skills loaded.")
            return
        
        print("\nAvailable Skills:")
        print("-" * 30)
        for i, (name, module) in enumerate(self.skills.items(), 1):
            description = getattr(module, '__doc__', 'No description available')
            if description:
                description = description.strip().split('\n')[0]  # First line only
            print(f"{i:2d}. {name:<20} - {description}")
        print()
    
    def run_skill(self, skill_identifier: str, *args, **kwargs):
        """Run a skill by name or number"""
        skill_module = None
        skill_name = None
        
        # Try to get skill by number
        if skill_identifier.isdigit():
            skill_num = int(skill_identifier)
            skill_names = list(self.skills.keys())
            if 1 <= skill_num <= len(skill_names):
                skill_name = skill_names[skill_num - 1]
                skill_module = self.skills[skill_name]
        
        # Try to get skill by name
        elif skill_identifier in self.skills:
            skill_name = skill_identifier
            skill_module = self.skills[skill_identifier]
        
        if not skill_module:
            print(f"✗ Skill '{skill_identifier}' not found")
            self.logger.warning(f"Attempted to run unknown skill: {skill_identifier}")
            if self.audit_logger:
                self.audit_logger.log_user_action(f"Failed skill execution", {
                    'skill_identifier': skill_identifier,
                    'reason': 'skill not found'
                })
            return
        
        try:
            self.logger.info(f"Executing skill: {skill_name} with args: {args}")
            if self.audit_logger:
                self.audit_logger.log_skill_execution(skill_name, list(args))
            
            result = skill_module.run(*args, **kwargs)
            print(f"✓ Skill '{skill_name}' completed")
            if result:
                print(f"Result: {result}")
            self.logger.info(f"Skill {skill_name} completed successfully")
            
            if self.audit_logger:
                self.audit_logger.log_skill_execution(skill_name, list(args), str(result) if result else None)
            
            return result
        except Exception as e:
            error_msg = f"Error running skill '{skill_name}': {e}"
            print(f"✗ {error_msg}")
            self.logger.error(f"{error_msg}\n{traceback.format_exc()}")
            
            if self.audit_logger:
                self.audit_logger.log_security_event(f"Skill execution error", {
                    'skill': skill_name,
                    'error': str(e)
                })
    
    def show_help(self):
        """Display help information"""
        help_text = """
Guardian Interpreter - Local Modular AI Agent
============================================

Commands:
  help                    - Show this help message
  skills                  - List all available skills
  skill <name/number>     - Run a specific skill
  config                  - Show current configuration
  status                  - Show system status
  logs                    - Show recent log entries
  nodie <prompt>          - Chat with the local AI (when LLM is loaded)
  quit, exit              - Exit the Guardian

Examples:
  skill 1                 - Run the first skill
  skill example_skill     - Run skill by name
  skill lan_scan 192.168.1.0/24  - Run skill with arguments
  nodie "What's my network status?"  - Ask the AI

Privacy Features:
  • All network requests are blocked by default (ALLOW_ONLINE=False)
  • All actions are logged to logs/guardian.log
  • Blocked network attempts logged to logs/blocked_calls.log
  • No telemetry, no auto-updates, no external APIs
        """
        print(help_text)
    
    def show_config(self):
        """Display current configuration (sanitized)"""
        print("\nCurrent Configuration:")
        print("-" * 30)
        print(f"Online Mode: {self.config.get('network', {}).get('ALLOW_ONLINE', False)}")
        print(f"Skills Auto-load: {self.config.get('skills', {}).get('auto_load', True)}")
        print(f"Log Level: {self.config.get('logging', {}).get('level', 'INFO')}")
        print(f"LLM Model: {self.config.get('llm', {}).get('model_path', 'Not configured')}")
        print()
    
    def show_status(self):
        """Display system status"""
        print("\nGuardian Status:")
        print("-" * 20)
        print(f"Skills Loaded: {len(self.skills)}")
        
        # LLM Status
        if self.llm:
            llm_info = self.llm.get_model_info()
            if llm_info['loaded']:
                print(f"LLM Status: Loaded ({llm_info.get('model_path', 'Unknown')})")
            else:
                print(f"LLM Status: Not loaded")
        else:
            print(f"LLM Status: Not initialized")
            
        print(f"Online Mode: {'ENABLED' if self.config.get('network', {}).get('ALLOW_ONLINE', False) else 'BLOCKED'}")
        print(f"Uptime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
    
    def show_recent_logs(self, lines: int = 10):
        """Show recent log entries"""
        log_file = self.config.get('logging', {}).get('main_log', 'logs/guardian.log')
        try:
            with open(log_file, 'r') as f:
                log_lines = f.readlines()
                recent_lines = log_lines[-lines:]
                print(f"\nRecent Log Entries (last {lines} lines):")
                print("-" * 40)
                for line in recent_lines:
                    print(line.strip())
                print()
        except FileNotFoundError:
            print(f"Log file {log_file} not found")
    
    def chat_with_nodie(self, prompt: str):
        """Chat with the local AI (Nodie)"""
        self.logger.info(f"User prompt: {prompt}")
        
        if self.audit_logger:
            self.audit_logger.log_llm_interaction(prompt)
        
        if not self.llm or not self.llm.is_loaded():
            response = "Nodie is not available. Please configure a GGUF model in config.yaml and ensure llama-cpp-python is installed."
            print(f"Nodie: {response}")
            self.logger.info(f"Nodie response: {response}")
            
            if self.audit_logger:
                self.audit_logger.log_llm_interaction(prompt, response)
            
            return response
        
        try:
            # Generate response using the local LLM
            response = self.llm.generate_response(prompt)
            print(f"Nodie: {response}")
            self.logger.info(f"Nodie response: {response}")
            
            if self.audit_logger:
                self.audit_logger.log_llm_interaction(prompt, response)
            
            return response
            
        except Exception as e:
            error_msg = f"Error communicating with Nodie: {e}"
            print(f"Nodie: {error_msg}")
            self.logger.error(error_msg)
            
            if self.audit_logger:
                self.audit_logger.log_security_event("LLM interaction error", {
                    'error': str(e),
                    'prompt_length': len(prompt)
                })
            
            return error_msg
    
    def run_cli(self):
        """Main CLI loop"""
        cli_config = self.config.get('cli', {})
        prompt_prefix = cli_config.get('prompt_prefix', 'Guardian> ')
        
        # Show initial information
        system_info = self.config.get('system', {})
        print(f"\n{system_info.get('name', 'Guardian Interpreter')} v{system_info.get('version', '1.0.0')}")
        print(f"Owner: {system_info.get('owner', 'Blackbox Matrix')}")
        print("Type 'help' for commands, 'quit' to exit")
        
        if cli_config.get('show_skill_list_on_start', True):
            self.list_skills()
        
        # Main command loop
        while self.running:
            try:
                user_input = input(prompt_prefix).strip()
                
                if not user_input:
                    continue
                
                # Log user input
                self.logger.info(f"User input: {user_input}")
                
                # Parse command
                parts = user_input.split()
                command = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []
                
                # Handle commands
                if command in ['quit', 'exit']:
                    self.running = False
                    print("Goodbye!")
                    self.logger.info("Guardian shutting down by user request")
                
                elif command == 'help':
                    self.show_help()
                
                elif command == 'skills':
                    self.list_skills()
                
                elif command == 'skill':
                    if args:
                        self.run_skill(args[0], *args[1:])
                    else:
                        print("Usage: skill <name/number> [arguments]")
                
                elif command == 'config':
                    self.show_config()
                
                elif command == 'status':
                    self.show_status()
                
                elif command == 'logs':
                    lines = int(args[0]) if args and args[0].isdigit() else 10
                    self.show_recent_logs(lines)
                
                elif command == 'nodie':
                    if args:
                        prompt = ' '.join(args)
                        self.chat_with_nodie(prompt)
                    else:
                        print("Usage: nodie <your prompt>")
                
                else:
                    print(f"Unknown command: {command}. Type 'help' for available commands.")
                    self.logger.warning(f"Unknown command attempted: {command}")
            
            except KeyboardInterrupt:
                print("\nUse 'quit' to exit gracefully.")
            except EOFError:
                self.running = False
                print("\nGoodbye!")
                self.logger.info("Guardian shutting down (EOF)")
            except Exception as e:
                print(f"Error: {e}")
                self.logger.error(f"CLI error: {e}\n{traceback.format_exc()}")

def main():
    """Main entry point"""
    print("Starting Guardian Interpreter...")
    
    try:
        guardian = GuardianInterpreter()
        guardian.load_skills()
        guardian.run_cli()
    except Exception as e:
        print(f"Fatal error: {e}")
        logging.error(f"Fatal error: {e}\n{traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()

