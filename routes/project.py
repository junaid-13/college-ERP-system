from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel
import os
import re
from utils.file_handler import create_directory, write_json, read_json
from services.feature_manager import set_current_feature


router = APIRouter()
PROJECTS_DIR = "projects"

class CreateProjectRequest(BaseModel):
    project_name: str
    system_prompt: str
    stack: str
    
def validate_project_name(name: str) -> str:
    if not re.match(r'^[A-Za-z0-9]+(?:[_-][A-Za-z0-9]+)*$', name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project name."
        )
    if ".." in name or "/" in name or "\\" in name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project name"
        )   
    return name


@router.post("/project", status_code=status.HTTP_201_CREATED)
def create_project(data: CreateProjectRequest):
    
    project_name = validate_project_name(data.project_name)
    project_path = os.path.join(PROJECTS_DIR, project_name)
    
    if os.path.isdir(project_path):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Project already exists"
        )
    
    try:
        # Create project directory
        create_directory(project_path)
        create_directory(os.path.join(project_path, "features"))
 

        # config.json
        config = {
            "project_name": project_name,
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
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        ) 
    return {"message": f"Project '{project_name}' created successfully."}


@router.post("/project/{project_name}/feature", status_code=status.HTTP_200_OK)
def update_feature(project_name: str, feature_name: str):
    project_name = validate_project_name(project_name)
    project_path = os.path.join(PROJECTS_DIR, project_name)
    
    if not os.path.isdir(project_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    feature_name = feature_name.strip()
    if not feature_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="feature_name is required"
        )

    try:
        # update features.json
        features = set_current_feature(project_name, feature_name)    
    
    
        # Update memory.json
        memory_path = os.path.join(project_path, "memory.json")
        memory = read_json(memory_path)
        if not memory:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Memory file missing or corrupted"
            )

        memory["current_feature"] = feature_name
        memory["last_task"] = f"Started {feature_name}"
    
        write_json(memory_path, memory)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update feature: {str(e)}"
        )
    return {
        "message": f"Switched to feature '{feature_name}'",
        "features": features
    }