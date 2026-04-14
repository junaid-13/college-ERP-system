from fastapi import APIRouter
from pydantic import BaseModel
import os
from utils.file_handler import create_directory, write_json

router = APIRouter()
PROJECTS_DIR = "projects"

class CreateProjectRequest(BaseModel):
    project_name: str
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