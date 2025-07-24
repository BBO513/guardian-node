import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

# guardian_interpreter/family_mcp_server.py
from mcp import Server
from guardian_interpreter.family_assistant import process_family_query, execute_family_skill, get_family_recommendations, analyze_family_security
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

server = Server("guardian-family-assistant")

@server.tool
def ask_family_question(query):
    logger.info(f"Processing family query: {query}")
    return process_family_query(query, child_safe=True, family_mode=True)

@server.tool
def run_family_skill(skill_name, *args):
    logger.info(f"Executing family skill: {skill_name}")
    return execute_family_skill(skill_name, *args, family_mode=True)

if __name__ == "__main__":
    server.run(host="localhost", port=8081, privacy_mode="strict", child_safe=True, family_mode=True)
