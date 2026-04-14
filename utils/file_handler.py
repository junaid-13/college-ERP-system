import os
import json

def create_directory(path: str):
    os.makedirs(path, exist_ok=True)
    
def write_json(path: str, data: dict):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
        
def read_json(path: str):
    if not os.path.exists(path):
        return None
    with open(path, 'r') as f:
        return json.load(f)