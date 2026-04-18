from fastapi import APIRouter
from pydantic import BaseModel, StringConstraints
from typing import Annotated
import os
from utils.file_handler import create_directory, write_json, read_json
from services.feature_manager import set_current_feature


router = APIRouter()
PROJECTS_DIR = "projects"

class CreateProjectRequest(BaseModel):
    project_name: Annotated[
        str,
        StringConstraints(pattern=r'^[A-Za-z0-9]+(?:[_-][A-Za-z0-9]+)*$')
    ]
    system_prompt: str
    stack: str
    
@router.post("/project")
def create_project(data: CreateProjectRequest):
    project_path = os.path.join(PROJECTS_DIR, data.project_name)
    
    if os.path.exists(project_path):
        return {"error": "Project already exists"}
    
    # Create project directory
    create_directory(project_path)
    create_directory(os.path.join(project_path, "features"))
    
    # config.json
    config = {
        "project_name": data.project_name,
        "system_prompt": data.system_prompt,
        "stack": data.stack
    }
    
    # memory.json
    memory = {
        "current_feature": None,
        "last_task": None,
        "project_summary": "Project initialized.",
        "last_updated": None
    }
    
    # features.json
    features = {
        "features": []
    }
    
    write_json(os.path.join(project_path, "config.json"), config)
    write_json(os.path.join(project_path, "memory.json"), memory)
    write_json(os.path.join(project_path, "features.json"), features)
        
    return {"message": f"Project '{data.project_name}' created successfully."}


@router.post("/project/{project_name}/feature")
def update_feature(project_name: str, feature_name: str):
    project_path = os.path.join(PROJECTS_DIR, project_name)
    
    if not os.path.exists(project_path):
        return {"error": "Project not found"}
    
    if not feature_name:
        return {"error": "feature_name is required"}

    # update features.json
    features = set_current_feature(project_name, feature_name)    
    
    
    # Update memory.json
    memory_path = os.path.join(project_path, "memory.json")
    if not memory:
        return {"error": "Memory file missing or corrupted"}
    memory = read_json(memory_path)
    
    memory["current_feature"] = feature_name
    memory["last_task"] = f"Started {feature_name}"
    
    write_json(memory_path, memory)
    return {
        "message": f"Switched to feature '{feature_name}'",
        "features": features
    }