def build_prompt(config: dict, user_prompt: str):
    return f"""
You are a senior full-stack developer.

project: {config['project_name']}
Stack: {config['stack']}

Instructions:
{config['system_prompt']}

user Request:
{user_prompt}

Provide clean, production-ready code.
"""