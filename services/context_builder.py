import os

WORKSPACE_DIR = "workspace"
MAX_FILE_SIZE = 5000

def read_file_safe(file_path: str):
    if not os.path.exists(file_path):
        return None
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read(MAX_FILE_SIZE)

def get_relevant_files(project_name: str, files: list[str] = None):
    """
    If user provides files -> use them
    Otherwise -> fallback to basic scan
    """
    
    project_path = os.path.join(WORKSPACE_DIR, project_name)
    
    collected = []
    
    # case 1: user provided files
    if files:
        for f in files:
            full_path = os.path.join(project_path, f)
            content = read_file_safe(full_path)
            if content:
                collected.append((f, content))
        return collected
    
    # case 2: fallback (basic scan)
    for root, _, filenames in os.walk(project_path):
        for name in filenames:
            full_path = os.path.join(root, name)
            content = read_file_safe(full_path)
            if content:
                rel_path = os.path.relpath(full_path, project_path)
                collected.append((rel_path, content))
        break
    return collected

def format_code_context(files):
    if not files:
        return "No relevant code provided."
    
    result = "\n\nRelevant code:\n"
    
    for path, content in files:
        result += f"\n--- {path} ---\n{content}\n"
    return result
