import yaml
from datetime import datetime
from skills import load_skills

try:
    from llama_cpp import Llama
except ImportError:
    Llama = None

# Load config
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)
ALLOW_ONLINE = config.get("ALLOW_ONLINE", False)
MODEL_PATH = config.get("MODEL_PATH", "./models/your-model.gguf")

# Logger
def log(msg, fname="guardian.log"):
    with open(f"logs/{fname}", "a") as f:
        f.write(f"[{datetime.now()}] {msg}\n")

# Call-home block
def outbound_request(url, data=None):
    if not ALLOW_ONLINE:
        log(f"BLOCKED CALL TO: {url}", "blocked_calls.log")
        return "ERROR: Internet is disabled."
    log(f"OUTBOUND REQUEST: {url} Data: {data}", "guardian.log")
    # (if allowed: actually send request)
    return "SENT"

# LLM
llm = None
if Llama:
    try:
        llm = Llama(model_path=MODEL_PATH)
    except Exception as e:
        log(f"Failed to load model: {e}")

def ask_nodie(prompt):
    if llm is None:
        return "LLM not loaded."
    result = llm(prompt, max_tokens=128)
    return result["choices"][0]["text"]

# Skills
skills = load_skills()

def dispatch_skill(skill_name, *args):
    if skill_name in skills:
        log(f"Skill called: {skill_name} with {args}")
        return skills[skill_name](*args)
    else:
        log(f"Unknown skill: {skill_name}")
        return "Skill not found."

def main():
    print("Guardian Interpreter - Nodie Offline Agent")
    print("Type 'help' for commands.")
    while True:
        cmd = input(">>> ").strip()
        if cmd == "exit": break
        elif cmd == "help":
            print("Commands:")
            print("  nodie <your prompt>      (Ask the LLM)")
            print("  skill <name> [args]     (Call protocol module)")
            print("  skills                  (List loaded skills)")
            print("  exit                    (Quit)")
        elif cmd.startswith("nodie "):
            prompt = cmd[6:].strip()
            print(ask_nodie(prompt))
        elif cmd.startswith("skill "):
            parts = cmd.split()
            name = parts[1]
            args = parts[2:]
            print(dispatch_skill(name, *args))
        elif cmd == "skills":
            print("Loaded skills:", ", ".join(skills.keys()))
        else:
            print("Unknown command. Type 'help'.")

if __name__ == "__main__":
    main()
