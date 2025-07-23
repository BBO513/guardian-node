"""
Child Education Skill for Family Cybersecurity
Generates age-appropriate cybersecurity education content, conversation starters,
and interactive learning activities for parents to use with their children.
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import random

class ChildEducationDatabase:
    """Database of age-appropriate cybersecurity education content"""
    
    def __init__(self):
        self.age_groups = {
            'preschool': {
                'age_range': '3-5 years',
                'key_concepts': [
                    'Stranger danger online',
                    'Asking permission before using devices',
                    'Not sharing personal information',
                    'Telling parents about scary things online'
                ],
                'activities': [
                    {
                        'name': 'Online Stranger Game',
                        'description': 'Role-play scenarios about talking to strangers online',
                        'materials': 'None needed',
                        'duration': '10-15 minutes',
                        'instructions': [
                            'Pretend to be someone online asking for their name',
                            'Teach them to say "I need to ask my parent first"',
                            'Practice with different scenarios',
                            'Praise them for asking permission'
                        ]
                    },
                    {
                        'name': 'Device Permission Chart',
                        'description': 'Visual chart showing when to ask before using devices',
                        'materials': 'Paper, stickers, crayons',
                        'duration': '20-30 minutes',
                        'instructions': [
                            'Draw pictures of different devices',
                            'Add "Ask First" stickers to each device',
                            'Let child decorate the chart',
                            'Hang it where they can see it'
                        ]
                    }
                ],
                'conversation_starters': [
                    "What should you do if someone online asks for your name?",
                    "Who should you tell if you see something scary on a screen?",
                    "What do we do before using mommy or daddy's phone?",
                    "Are people online the same as people we meet in person?"
                ]
            },
            'elementary': {
                'age_range': '6-10 years',
                'key_concepts': [
                    'Password safety and privacy',
                    'Recognizing inappropriate content',
                    'Understanding that not everything online is true',
                    'Cyberbullying awareness and response',
                    'Safe vs unsafe websites'
                ],
                'activities': [
                    {
                        'name': 'Password Superhero Game',
                        'description': 'Create superhero passwords that are strong and secret',
                        'materials': 'Paper, colored pencils',
                        'duration': '30-45 minutes',
                        'instructions': [
                            'Explain passwords are like secret superhero identities',
                            'Create a strong password using favorite things',
                            'Draw a picture to remember it (without writing the password)',
                            'Practice keeping it secret from friends'
                        ]
                    },
                    {
                        'name': 'True or False Internet Detective',
                        'description': 'Learn to question information found online',
                        'materials': 'Printed examples of real/fake news for kids',
                        'duration': '20-30 minutes',
                        'instructions': [
                            'Show examples of obviously fake kid-friendly stories',
                            'Ask "Does this seem real or made up?"',
                            'Discuss clues that something might not be true',
                            'Practice asking "How do we know this is real?"'
                        ]
                    },
                    {
                        'name': 'Cyberbullying Response Practice',
                        'description': 'Role-play appropriate responses to online meanness',
                        'materials': 'None needed',
                        'duration': '15-25 minutes',
                        'instructions': [
                            'Act out scenarios of online meanness',
                            'Practice responses: "Stop, Block, Tell"',
                            'Discuss feelings and how to handle them',
                            'Emphasize telling a trusted adult'
                        ]
                    }
                ],
                'conversation_starters': [
                    "What makes a password strong like a superhero?",
                    "How can we tell if something online is real or pretend?",
                    "What would you do if someone was mean to you online?",
                    "Why is it important to keep passwords secret?",
                    "What websites are safe for kids your age?"
                ]
            },
            'middle_school': {
                'age_range': '11-13 years',
                'key_concepts': [
                    'Social media privacy and safety',
                    'Digital footprint awareness',
                    'Recognizing and avoiding scams',
                    'Appropriate online behavior and digital citizenship',
                    'Understanding consequences of online actions'
                ],
                'activities': [
                    {
                        'name': 'Digital Footprint Tracking',
                        'description': 'Visualize how online actions leave permanent traces',
                        'materials': 'Sand tray, toy figures, camera',
                        'duration': '45-60 minutes',
                        'instructions': [
                            'Walk toy figures through sand, leaving footprints',
                            'Explain how online actions leave similar traces',
                            'Discuss what kind of digital footprints they want to leave',
                            'Take photos to show how footprints remain'
                        ]
                    },
                    {
                        'name': 'Social Media Privacy Audit',
                        'description': 'Review and adjust privacy settings together',
                        'materials': 'Device with social media apps',
                        'duration': '30-45 minutes',
                        'instructions': [
                            'Go through privacy settings on their accounts',
                            'Explain what each setting means',
                            'Discuss who should see their posts',
                            'Set up appropriate restrictions together'
                        ]
                    },
                    {
                        'name': 'Scam Detective Challenge',
                        'description': 'Learn to identify common online scams targeting teens',
                        'materials': 'Examples of teen-targeted scams',
                        'duration': '30-40 minutes',
                        'instructions': [
                            'Show examples of "free" game offers, fake contests',
                            'Discuss red flags: "too good to be true" offers',
                            'Practice saying no to suspicious requests',
                            'Create a family code word for scam situations'
                        ]
                    }
                ],
                'conversation_starters': [
                    "What do you think your digital footprint says about you?",
                    "How do you decide what to share on social media?",
                    "What would you do if someone offered you something free online?",
                    "How can we tell if an online friend is really who they say they are?",
                    "What are the consequences of posting something mean online?"
                ]
            },
            'high_school': {
                'age_range': '14-18 years',
                'key_concepts': [
                    'Advanced privacy protection',
                    'Understanding online predators and manipulation',
                    'Digital reputation management',
                    'Secure communication practices',
                    'Preparing for adult digital responsibilities'
                ],
                'activities': [
                    {
                        'name': 'College Application Digital Cleanup',
                        'description': 'Audit and clean up online presence for college/job applications',
                        'materials': 'Computer, list of social media accounts',
                        'duration': '60-90 minutes',
                        'instructions': [
                            'Search their name on Google together',
                            'Review all social media profiles',
                            'Delete inappropriate content',
                            'Discuss professional online presence'
                        ]
                    },
                    {
                        'name': 'Manipulation Tactics Workshop',
                        'description': 'Learn to recognize psychological manipulation online',
                        'materials': 'Examples of manipulation techniques',
                        'duration': '45-60 minutes',
                        'instructions': [
                            'Discuss common manipulation tactics',
                            'Role-play scenarios with peer pressure',
                            'Practice assertive responses',
                            'Create personal safety boundaries'
                        ]
                    },
                    {
                        'name': 'Secure Communication Setup',
                        'description': 'Set up secure messaging and email practices',
                        'materials': 'Smartphone, computer',
                        'duration': '30-45 minutes',
                        'instructions': [
                            'Install secure messaging apps',
                            'Set up two-factor authentication',
                            'Discuss when to use secure communication',
                            'Practice recognizing phishing attempts'
                        ]
                    }
                ],
                'conversation_starters': [
                    "How might your online presence affect your future opportunities?",
                    "What are some ways people might try to manipulate you online?",
                    "How do you balance privacy with staying connected to friends?",
                    "What would you do if someone asked you to keep an online relationship secret?",
                    "How can you help younger kids stay safe online?"
                ]
            }
        }
        
        self.safety_scenarios = {
            'stranger_contact': {
                'scenario': 'A stranger online asks for personal information',
                'age_responses': {
                    'preschool': 'Tell them to ask mommy or daddy first',
                    'elementary': 'Never give personal information to strangers online',
                    'middle_school': 'Block the person and tell a parent immediately',
                    'high_school': 'Recognize this as a red flag and report if necessary'
                }
            },
            'cyberbullying': {
                'scenario': 'Someone is being mean or threatening online',
                'age_responses': {
                    'preschool': 'Tell a grown-up right away',
                    'elementary': 'Don\'t respond, save evidence, tell a trusted adult',
                    'middle_school': 'Block, report, document, and involve parents/school',
                    'high_school': 'Document evidence, report to platform, involve authorities if needed'
                }
            },
            'inappropriate_content': {
                'scenario': 'Accidentally seeing inappropriate or scary content',
                'age_responses': {
                    'preschool': 'Close the screen and tell mommy or daddy',
                    'elementary': 'Navigate away immediately and tell a parent',
                    'middle_school': 'Close content, use parental controls, discuss with parents',
                    'high_school': 'Understand how to avoid and report inappropriate content'
                }
            }
        }

class ChildEducationFormatter:
    """Formats educational content for parents and children"""
    
    @staticmethod
    def format_age_appropriate_guide(age_group: str, content: Dict[str, Any]) -> str:
        """Format a complete age-appropriate education guide"""
        guide = f"👶 **Cybersecurity Education for {content['age_range']}**\n\n"
        
        # Key concepts
        guide += "🎯 **Key Concepts to Teach:**\n"
        for concept in content['key_concepts']:
            guide += f"• {concept}\n"
        guide += "\n"
        
        # Activities
        guide += "🎮 **Fun Learning Activities:**\n\n"
        for activity in content['activities']:
            guide += f"**{activity['name']}** ({activity['duration']})\n"
            guide += f"*{activity['description']}*\n"
            guide += f"**Materials needed:** {activity['materials']}\n"
            guide += "**Instructions:**\n"
            for i, instruction in enumerate(activity['instructions'], 1):
                guide += f"   {i}. {instruction}\n"
            guide += "\n"
        
        # Conversation starters
        guide += "💬 **Conversation Starters:**\n"
        for starter in content['conversation_starters']:
            guide += f"• \"{starter}\"\n"
        guide += "\n"
        
        return guide
    
    @staticmethod
    def format_scenario_guidance(scenario_name: str, scenario_data: Dict[str, Any]) -> str:
        """Format guidance for handling specific safety scenarios"""
        guidance = f"🚨 **Safety Scenario: {scenario_data['scenario']}**\n\n"
        
        guidance += "**Age-Appropriate Responses:**\n\n"
        
        age_labels = {
            'preschool': '👶 Preschool (3-5 years)',
            'elementary': '🧒 Elementary (6-10 years)',
            'middle_school': '👦 Middle School (11-13 years)',
            'high_school': '👨 High School (14-18 years)'
        }
        
        for age_group, response in scenario_data['age_responses'].items():
            label = age_labels.get(age_group, age_group.title())
            guidance += f"**{label}:**\n"
            guidance += f"   {response}\n\n"
        
        return guidance
    
    @staticmethod
    def format_activity_instructions(activity: Dict[str, Any]) -> str:
        """Format detailed instructions for a specific activity"""
        instructions = f"🎯 **Activity: {activity['name']}**\n\n"
        instructions += f"**Description:** {activity['description']}\n"
        instructions += f"**Duration:** {activity['duration']}\n"
        instructions += f"**Materials:** {activity['materials']}\n\n"
        
        instructions += "**Step-by-Step Instructions:**\n"
        for i, step in enumerate(activity['instructions'], 1):
            instructions += f"{i}. {step}\n"
        
        instructions += "\n💡 **Tip:** Make this fun and interactive! Let your child lead the conversation when possible."
        
        return instructions

class ChildEducationSkill:
    """Main child education skill class"""
    
    def __init__(self):
        self.education_db = ChildEducationDatabase()
        self.formatter = ChildEducationFormatter()
    
    def get_age_appropriate_content(self, age_group: str) -> str:
        """Get comprehensive education content for specific age group"""
        if age_group not in self.education_db.age_groups:
            return self._format_age_group_options()
        
        content = self.education_db.age_groups[age_group]
        return self.formatter.format_age_appropriate_guide(age_group, content)
    
    def get_safety_scenario_guidance(self, scenario_query: str = None) -> str:
        """Get guidance for handling specific safety scenarios"""
        if not scenario_query:
            return self._format_all_scenarios()
        
        # Find matching scenario
        scenario_query_lower = scenario_query.lower()
        for scenario_id, scenario_data in self.education_db.safety_scenarios.items():
            if (scenario_id.replace('_', ' ') in scenario_query_lower or
                any(word in scenario_query_lower for word in scenario_id.split('_'))):
                return self.formatter.format_scenario_guidance(scenario_id, scenario_data)
        
        # No specific match found
        return self._format_scenario_not_found(scenario_query)
    
    def get_activity_instructions(self, activity_query: str, age_group: str = None) -> str:
        """Get detailed instructions for a specific activity"""
        activity_query_lower = activity_query.lower()
        
        # Search through all age groups or specific age group
        age_groups_to_search = [age_group] if age_group else self.education_db.age_groups.keys()
        
        for age in age_groups_to_search:
            if age not in self.education_db.age_groups:
                continue
                
            for activity in self.education_db.age_groups[age]['activities']:
                if activity_query_lower in activity['name'].lower():
                    return self.formatter.format_activity_instructions(activity)
        
        return self._format_activity_not_found(activity_query)
    
    def get_conversation_starters(self, age_group: str = None, topic: str = None) -> str:
        """Get conversation starters for cybersecurity discussions"""
        if age_group and age_group not in self.education_db.age_groups:
            return self._format_age_group_options()
        
        starters = "💬 **Cybersecurity Conversation Starters**\n\n"
        
        if age_group:
            # Specific age group
            content = self.education_db.age_groups[age_group]
            starters += f"**For {content['age_range']}:**\n"
            for starter in content['conversation_starters']:
                starters += f"• \"{starter}\"\n"
        else:
            # All age groups
            for age, content in self.education_db.age_groups.items():
                starters += f"**{content['age_range']}:**\n"
                for starter in content['conversation_starters'][:3]:  # Limit to 3 per age group
                    starters += f"• \"{starter}\"\n"
                starters += "\n"
        
        starters += "\n💡 **Tips for Great Conversations:**\n"
        starters += "• Ask open-ended questions\n"
        starters += "• Listen without judgment\n"
        starters += "• Share age-appropriate examples\n"
        starters += "• Make it a regular discussion, not a one-time talk\n"
        
        return starters
    
    def get_general_education_overview(self) -> str:
        """Get general overview of child cybersecurity education"""
        overview = "👨‍👩‍👧‍👦 **Family Cybersecurity Education Guide**\n\n"
        overview += "Teaching children about online safety is crucial in today's digital world. "
        overview += "Here's how to approach cybersecurity education by age group:\n\n"
        
        for age_group, content in self.education_db.age_groups.items():
            overview += f"**{content['age_range']}:**\n"
            overview += f"• Focus: {', '.join(content['key_concepts'][:2])}\n"
            overview += f"• Activities: {len(content['activities'])} fun learning activities available\n"
            overview += f"• Key approach: {self._get_age_approach(age_group)}\n\n"
        
        overview += "💡 **Ask me for specific guidance like:**\n"
        overview += "• \"Show me activities for elementary kids\"\n"
        overview += "• \"How do I handle cyberbullying scenarios?\"\n"
        overview += "• \"Give me conversation starters for teens\"\n"
        
        return overview
    
    def _get_age_approach(self, age_group: str) -> str:
        """Get the key educational approach for each age group"""
        approaches = {
            'preschool': 'Simple rules and asking permission',
            'elementary': 'Fun activities and clear boundaries',
            'middle_school': 'Interactive discussions and real scenarios',
            'high_school': 'Practical skills and adult preparation'
        }
        return approaches.get(age_group, 'Age-appropriate guidance')
    
    def _format_age_group_options(self) -> str:
        """Format available age group options"""
        options = "I can provide cybersecurity education guidance for these age groups:\n\n"
        
        for age_group, content in self.education_db.age_groups.items():
            options += f"• **{age_group.replace('_', ' ').title()}** ({content['age_range']})\n"
        
        options += "\nPlease specify an age group for detailed guidance!"
        
        return options
    
    def _format_all_scenarios(self) -> str:
        """Format all available safety scenarios"""
        scenarios = "🚨 **Common Safety Scenarios and Responses**\n\n"
        
        for scenario_id, scenario_data in self.education_db.safety_scenarios.items():
            scenarios += f"**{scenario_data['scenario']}**\n"
            scenarios += "Quick responses by age:\n"
            for age, response in scenario_data['age_responses'].items():
                age_label = age.replace('_', ' ').title()
                scenarios += f"• {age_label}: {response}\n"
            scenarios += "\n"
        
        scenarios += "💡 Ask me about any specific scenario for detailed guidance!"
        
        return scenarios
    
    def _format_scenario_not_found(self, query: str) -> str:
        """Format response when scenario is not found"""
        response = f"I couldn't find specific guidance for '{query}'. "
        response += "I can help with these common scenarios:\n\n"
        
        for scenario_id, scenario_data in self.education_db.safety_scenarios.items():
            response += f"• {scenario_data['scenario']}\n"
        
        response += "\nPlease ask about one of these scenarios!"
        
        return response
    
    def _format_activity_not_found(self, query: str) -> str:
        """Format response when activity is not found"""
        response = f"I couldn't find an activity matching '{query}'. "
        response += "Here are some available activities:\n\n"
        
        for age_group, content in self.education_db.age_groups.items():
            response += f"**{content['age_range']}:**\n"
            for activity in content['activities']:
                response += f"• {activity['name']}\n"
        
        response += "\nPlease ask about a specific activity name!"
        
        return response

def run(*args, **kwargs):
    """
    Main entry point for child education skill
    
    Args:
        *args: Query and additional arguments
        **kwargs: Additional context (age_group, etc.)
    
    Returns:
        str: Child cybersecurity education content and guidance
    """
    try:
        education_skill = ChildEducationSkill()
        
        # Handle case where no query is provided
        if not args:
            return education_skill.get_general_education_overview()
        
        # Parse arguments
        query = " ".join(args).strip().lower()
        
        # Detect age group in query
        age_group = None
        age_keywords = {
            'preschool': ['preschool', 'toddler', '3', '4', '5', 'young'],
            'elementary': ['elementary', 'primary', '6', '7', '8', '9', '10', 'grade school'],
            'middle_school': ['middle school', 'middle', 'tween', '11', '12', '13'],
            'high_school': ['high school', 'teen', 'teenager', '14', '15', '16', '17', '18']
        }
        
        for age, keywords in age_keywords.items():
            if any(keyword in query for keyword in keywords):
                age_group = age
                break
        
        # Handle different types of queries
        if any(word in query for word in ['activity', 'activities', 'game', 'exercise']):
            if 'activity' in query and age_group:
                # Extract activity name from query
                activity_query = query.replace('activity', '').replace('activities', '')
                for age_keyword in age_keywords.get(age_group, []):
                    activity_query = activity_query.replace(age_keyword, '')
                activity_query = activity_query.strip()
                
                if activity_query:
                    return education_skill.get_activity_instructions(activity_query, age_group)
            
            # General activities request
            if age_group:
                return education_skill.get_age_appropriate_content(age_group)
            else:
                return education_skill.get_general_education_overview()
        
        elif any(word in query for word in ['conversation', 'talk', 'discuss', 'questions']):
            return education_skill.get_conversation_starters(age_group)
        
        elif any(word in query for word in ['scenario', 'situation', 'emergency', 'problem']):
            scenario_query = query
            # Remove common words to get scenario focus
            for word in ['scenario', 'situation', 'what', 'if', 'how', 'handle']:
                scenario_query = scenario_query.replace(word, '')
            scenario_query = scenario_query.strip()
            
            return education_skill.get_safety_scenario_guidance(scenario_query)
        
        elif age_group:
            # Age-specific content request
            return education_skill.get_age_appropriate_content(age_group)
        
        elif any(word in query for word in ['overview', 'general', 'all', 'summary']):
            return education_skill.get_general_education_overview()
        
        else:
            # Try to match query to specific content
            if any(word in query for word in ['stranger', 'unknown', 'contact']):
                return education_skill.get_safety_scenario_guidance('stranger contact')
            elif any(word in query for word in ['bully', 'mean', 'harassment']):
                return education_skill.get_safety_scenario_guidance('cyberbullying')
            elif any(word in query for word in ['inappropriate', 'scary', 'bad content']):
                return education_skill.get_safety_scenario_guidance('inappropriate content')
            else:
                return education_skill.get_general_education_overview()
    
    except Exception as e:
        # Graceful error handling
        error_response = "I'm sorry, I encountered an issue while providing child education guidance. "
        error_response += "Please try asking about specific age groups like 'elementary' or 'teens', "
        error_response += "or topics like 'activities', 'conversation starters', or 'safety scenarios'."
        
        # Log the error for debugging
        print(f"Child Education Skill Error: {e}")
        
        return error_response

# Skill metadata
__doc__ = "Generates age-appropriate cybersecurity education content and activities for families"
__version__ = "1.0.0"
__author__ = "Guardian Family Assistant"
__category__ = "child_education"