from fastapi import APIRouter
from pydantic import BaseModel
import os

from utils.file_handler import read_json
from services.ollama_client import generate_from_ollama
from services.prompt_builder import build_prompt
from services.memory_manager import load_memory, update_memory
from services.context_builder import get_relevant_files, format_code_context
from services.feature_manager import load_features
from utils.response_cleaner import clean_response

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
    features = load_features(project_name)

    # get relevant files
    files = get_relevant_files(project_name, body.files)

    code_context = format_code_context(files)

    final_prompt = build_prompt(
        config,
        memory,
        features,
        code_context,
        body.prompt
    )

    raw_result = generate_from_ollama(final_prompt)
    result = clean_response(raw_result)
    result = result.replace("\\n", "\n")
    
    updated_memory = update_memory(
        project_name,
        memory,
        body.prompt,
        result
    )

    return {
        "result": result,
        "memory": updated_memory,
        "used_files": [f[0] for f in files]
    }