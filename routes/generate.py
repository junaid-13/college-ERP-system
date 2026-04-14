from fastapi import APIRouter
from pydantic import BaseModel
import os

from utils.file_handler import read_json
from services.ollama_client import generate_from_ollama
from services.prompt_builder import build_prompt

router = APIRouter()

PROJECTS_DIR = "projects"

class GenerateRequest(BaseModel):
    prompt: str
    

@router.post("/generate/{project_name}")
def generate(project_name: str, body: GenerateRequest):
    project_path = os.path.join(PROJECTS_DIR, project_name)
    
    
    if not os.path.exists(project_path):
        return {"error": "Project not found"}
    
    config = read_json(os.path.join(project_path, "config.json"))
    
    final_prompt = build_prompt(config, body.prompt)
    
    result = generate_from_ollama(final_prompt)
    
    return {"result": result}