from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
import os
import re
from functools import lru_cache
from utils.file_handler import read_json
from services.ollama_client import generate_from_ollama
from services.prompt_builder import build_prompt
from services.memory_manager import load_memory, update_memory
from services.context_builder import get_relevant_files, format_code_context
from services.feature_manager import load_features
from utils.response_cleaner import clean_response

router = APIRouter()

PROJECTS_DIR = "projects"

def validate_project_name(name: str) -> str:
    if not re.match(r"^[a-zA-Z0-9_-]+(?:[_-][A-Za-z0-9]+)*$", name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project name."
        )
    return name

def validate_files(files: list[str]) -> list[str]:
    safe_files = []
    for f in files:
        if ".." in f or "/" in f or "\\" in f:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file path: {f}"
            )
        safe_files.append(f)
    return safe_files

class GenerateRequest(BaseModel):
    prompt: str
    files: list[str] = Field(default_factory=list)

@lru_cache(maxsize=100)
def get_cached_config(project_path: str):
    return read_json(os.path.join(project_path, "config.json"))

@lru_cache(maxsize=100)
def get_cached_features(project_name: str):
    return load_features(project_name)

@router.post("/generate/{project_name}")
async def generate(project_name: str, body: GenerateRequest):
    project_name = validate_project_name(project_name)
    project_path = os.path.join(PROJECTS_DIR, project_name)

    if not os.path.exists(project_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found."
        )
        
    try:
        config = get_cached_config(project_path)
        if not config:
            raise ValueError("Missing or invalid config.json")

        memory = load_memory(project_name)
        if not memory:
            raise ValueError("Missing or invalid memory.json")

        features = get_cached_features(project_name)

        safe_files = validate_files(body.files)
        files = get_relevant_files(project_name, safe_files)

        code_context = format_code_context(files)


        final_prompt = build_prompt(
            config,
            memory,
            features,
            code_context,
            body.prompt
        )


        raw_result = generate_from_ollama(final_prompt)

        if not raw_result:
            raise ValueError("Empty response from generation service")


        result = clean_response(raw_result)

        if isinstance(result, str):
            result = result.strip()


        try:
            updated_memory = update_memory(
                project_name,
                memory,
                body.prompt,
                result
            )
        except Exception:
            updated_memory = memory  

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Generation failed: {str(e)}"
        )
    return {
        "result": result,
        "memory": updated_memory,
        "used_files": [f[0] for f in files]
    }
 
''''
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
    }'''