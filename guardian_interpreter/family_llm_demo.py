"""
Family-Friendly LLM Demo
Demonstrates how to use the enhanced Guardian LLM with family-friendly prompts
"""

import logging
import yaml
from llm_integration import create_llm
from family_llm_prompts import FamilyContext, ChildSafetyLevel


def main():
    """Demonstrate family-friendly LLM capabilities"""
    
    print("=== Guardian Node Family Assistant Demo ===\n")
    
    # Set up logging
    logging.basicConfig(level=logging.WARNING)  # Reduce log noise for demo
    logger = logging.getLogger(__name__)
    
    # Load configuration
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print("Configuration file not found, using defaults...")
        config = {'llm': {'model_path': 'models/your-model.gguf'}}
    
    # Create LLM instance
    llm = create_llm(config, logger)
    
    # Load model
    print("Loading AI model...")
    success = llm.load_model()
    
    if not success or not llm.is_loaded():
        print("⚠️  No AI model loaded - switching to demo mode with mock responses")
        # Create MockLLM for demo purposes
        from llm_integration import MockLLM
        llm = MockLLM(config, logger)
        llm.load_model()
        print("✅ Demo mode activated\n")
    else:
        print("✅ AI model loaded successfully\n")
    
    # Demo scenarios
    scenarios = [
        {
            'title': 'General Family Cybersecurity Question',
            'prompt': 'How can I protect my family from online threats?',
            'context': FamilyContext.GENERAL,
            'child_safe': False
        },
        {
            'title': 'Child Education (Age-Appropriate)',
            'prompt': 'What is a computer virus and how do I stay safe?',
            'context': FamilyContext.CHILD_EDUCATION,
            'child_safe': True,
            'safety_level': ChildSafetyLevel.STRICT
        },
        {
            'title': 'Parent Guidance',
            'prompt': 'How do I set up parental controls on our devices?',
            'context': FamilyContext.PARENT_GUIDANCE,
            'child_safe': False
        },
        {
            'title': 'Device Security Help',
            'prompt': 'What security settings should I enable on my smartphone?',
            'context': FamilyContext.DEVICE_SECURITY,
            'child_safe': False
        },
        {
            'title': 'Threat Explanation (Family-Friendly)',
            'prompt': 'I heard about phishing attacks. What are they?',
            'context': FamilyContext.THREAT_EXPLANATION,
            'child_safe': False
        }
    ]
    
    # Run demo scenarios
    for i, scenario in enumerate(scenarios, 1):
        print(f"--- Scenario {i}: {scenario['title']} ---")
        print(f"Question: {scenario['prompt']}")
        print(f"Context: {scenario['context'].value}")
        
        if scenario['child_safe']:
            print(f"Child Safety: {scenario.get('safety_level', ChildSafetyLevel.STANDARD).value}")
        
        print("\nNodie's Response:")
        
        # Generate family-friendly response
        response = llm.generate_family_response(
            prompt=scenario['prompt'],
            context=scenario['context'],
            child_safe_mode=scenario['child_safe'],
            safety_level=scenario.get('safety_level', ChildSafetyLevel.STANDARD)
        )
        
        # Display response with word wrapping
        words = response.split()
        line = ""
        for word in words:
            if len(line + word) > 80:
                print(line)
                line = word + " "
            else:
                line += word + " "
        if line:
            print(line)
        
        print("\n" + "="*80 + "\n")
    
    # Demo with family profile
    print("--- Personalized Response Demo ---")
    print("Using family profile for personalized guidance...")
    
    family_profile = {
        'members': [
            {'age_group': 'child', 'tech_skill_level': 'beginner'},
            {'age_group': 'teen', 'tech_skill_level': 'intermediate'},
            {'age_group': 'adult', 'tech_skill_level': 'intermediate'}
        ],
        'devices': [
            {'device_type': 'smartphone'},
            {'device_type': 'tablet'},
            {'device_type': 'computer'}
        ],
        'security_preferences': {
            'threat_tolerance': 'low'
        }
    }
    
    print("Family Profile:")
    print("- Child (beginner tech skills)")
    print("- Teen (intermediate tech skills)")  
    print("- Adult (intermediate tech skills)")
    print("- Devices: smartphone, tablet, computer")
    print("- Security preference: cautious (low risk tolerance)")
    print()
    
    personalized_response = llm.generate_family_response(
        prompt="What are the most important security steps for our family?",
        context=FamilyContext.GENERAL,
        family_profile=family_profile
    )
    
    print("Nodie's Personalized Response:")
    words = personalized_response.split()
    line = ""
    for word in words:
        if len(line + word) > 80:
            print(line)
            line = word + " "
        else:
            line += word + " "
    if line:
        print(line)
    
    print("\n" + "="*80)
    print("Demo complete! The Guardian Node Family Assistant is ready to help")
    print("your family stay safe online with personalized, age-appropriate guidance.")
    print("="*80)


if __name__ == "__main__":
    main()