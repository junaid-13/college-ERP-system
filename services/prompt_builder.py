def build_prompt(config: dict, memory: dict, user_prompt: str):
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

user Request:
{user_prompt}

Continue the project intelligently based on current progress.
Provide clean, production-ready code.
"""