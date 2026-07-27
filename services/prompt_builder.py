def build_prompt(config, memory, features, code_context, user_prompt):
    completed = [
        f["name"] for f in features["features"]
        if f["status"] == "completed"
    ]

    return f"""
You are a senior full-stack developer.

Project: {config['project_name']}
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

User Request:
{user_prompt}

IMPORTANT OUTPUT FORMAT:

1. Always structure your response like this:

### Code
<ONLY code inside proper code block with language>

### Explanation
<clear explanation>

### Next Steps
<what to do next>

2. Code MUST:
- be inside triple backticks
- include language (e.g. ```js, ```python)
- be clean and properly formatted

3. DO NOT mix explanation inside code

4. DO NOT return JSON

5. DO NOT skip sections

Follow this strictly.
"""
# Continue the project intelligently based on current progress.
# The above line has been removed. If want to reuse then you can add it above the provide clean, production-ready code.

# If context is insufficient, ask for specific files.
# This line also removed.