import os
import importlib

def load_skills():
    skills = {}
    skill_dir = os.path.dirname(__file__)
    for file in os.listdir(skill_dir):
        if file.endswith('.py') and file != '__init__.py':
            modname = file[:-3]
            module = importlib.import_module(f"skills.{modname}")
            if hasattr(module, "run"):
                skills[modname] = module.run
    return skills
