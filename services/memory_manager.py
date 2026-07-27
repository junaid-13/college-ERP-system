import os
from utils.file_handler import read_json,write_json
from services.ollama_client import generate_from_ollama

PROJECTS_DIR = "projects"

def load_memory(project_name: str):
    path = os.path.join(PROJECTS_DIR, project_name, "memory.json")
    return read_json(path)

def save_memory(project_name: str, memory: dict):
    path = os.path.join(PROJECTS_DIR, project_name, "memory.json")
    write_json(path, memory)
    
def update_memory(project_name: str, old_memory: dict, user_prompt: str, ai_response: str):
    """
    Use AI to update memory intelligently
    """
    
    memory_prompt = f"""
    You are managing project memory for a software development project.memoryview
    
    Previous Memory:
    {old_memory}
    
    User Request:
    {user_prompt}
    
    AI Response:
    {ai_response}
    
    Update the memory in JSON format with:
    - current_feature
    - last_task
    - project_summary
    
    Return ONLY JSON.
    """
    
    updated = generate_from_ollama(memory_prompt)
    
    try:
        import json
        new_memory = json.loads(updated)
    except:
        # fallback if parsing fails
        new_memory = old_memory
        
    save_memory(project_name, new_memory)
    
    return new_memory   