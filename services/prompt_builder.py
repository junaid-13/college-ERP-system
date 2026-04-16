def build_prompt(config: dict, memory: dict, features: dict, code_context: str,user_prompt: str):
    completed = [
        f["name"] for f in features["features"]
        if f["status"] == "completed"
    ]
    return f"""
You are a senior full-stack developer.

project: {config['project_name']}
Stack: {config['stack']}

System Instructions:
{config['system_prompt']}

Project Summary:
{memory.get('project_summary')}

Current Feature:
{memory.get('current_feature')}

Last Task:
{memory.get('last_task')}

Completed Features:
{completed}

{code_context}

user Request:
{user_prompt}

Continue the current feature intelligently.
If needed, ask for missing files.

Provide clean, production-ready code.
"""
# Continue the project intelligently based on current progress.
# The above line has been removed. If want to reuse then you can add it above the provide clean, production-ready code.

# If context is insufficient, ask for specific files.
# This line also removed.