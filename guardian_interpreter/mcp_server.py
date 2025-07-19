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
