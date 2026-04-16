from logging import config

from fastapi import APIRouter
from pydantic import BaseModel
import os

from utils.file_handler import read_json
from services.ollama_client import generate_from_ollama
from services.prompt_builder import build_prompt
from services.memory_manager import load_memory, update_memory
from services.context_builder import get_relevant_files, format_code_context

router = APIRouter()

PROJECTS_DIR = "projects"

class GenerateRequest(BaseModel):
    prompt: str
    files: list[str] = []
    

@router.post("/generate/{project_name}")
def generate(project_name: str, body: GenerateRequest):
    project_path = os.path.join(PROJECTS_DIR, project_name)
    
    
    if not os.path.exists(project_path):
        return {"error": "Project not found"}
    
    config = read_json(os.path.join(project_path, "config.json"))
    memory = load_memory(project_name)
    
    # get relevant files
    files = get_relevant_files(project_name, body.files)
    
    print("got relevant files")
    # build context
    code_context = format_code_context(files)
    
    print("got the code context.")
    # build prompt
    final_prompt = build_prompt(config, memory, code_context, body.prompt)
    print("Got the final prompt.")
    result = generate_from_ollama(final_prompt)
    print("Got the result from ollama.")
    
    update_memory(
        project_name,
        memory,
        body.prompt,
        result
    )
    
    return {"result": result,
            "memory": update_memory,
            "used_files": [f[0] for f in files]
    }