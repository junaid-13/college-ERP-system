def build_prompt(config: dict, memory: dict, code_context: str,user_prompt: str):
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

{code_context}

user Request:
{user_prompt}

If context is insufficient, ask for specific files.
Provide clean, production-ready code.
"""
# Continue the project intelligently based on current progress.
# The above line has been removed. If want to reuse then you can add it above the provide clean, production-ready code.