import os
from utils.file_handler import read_json, write_json

PROJECT_DIR = "projects"

def load_features(project_name):
    path = os.path.join(PROJECT_DIR, project_name, "features.json")
    data = read_json(path)

    if not data:
        data = {"features": []}
        write_json(path, data)

    return data

def save_features(project_name: str, data: dict):
    path = os.path.join(PROJECT_DIR, project_name, "features.json")
    write_json(path, data)
    
def set_current_feature(project_name: str, feature_name: str):
    data = load_features(project_name)
    
    # mark all in_progress -> completed
    for f in data["features"]:
        if f["status"] == "in_progress":
            f["status"] = "completed"
            
    # check if feature exists
    found = False
    for f in data["features"]:
        if f["name"] == feature_name:
            f["status"] = "in_progress"
            found = True
            
    if not found:
        data["features"].append({
            "name": feature_name,
            "status": "in_progress"
        })
        
    save_features(project_name, data)
    
    return data