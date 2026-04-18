import os
import shutil
import sys
import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import patch

# Fix import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app

client = TestClient(app)
PROJECTS_DIR = "projects"


# ----------------------------
# Helper cleanup
# ----------------------------
def cleanup_project(name):
    path = os.path.join(PROJECTS_DIR, name)
    if os.path.exists(path):
        shutil.rmtree(path)


# ----------------------------
# 1. Success case
# ----------------------------
def test_create_project_success():
    name = "test_project"

    data = {
        "project_name": name,
        "system_prompt": "Test prompt",
        "stack": "fastapi"
    }

    response = client.post("/project", json=data)

    assert response.status_code == 201
    assert "created successfully" in response.json()["message"]

    project_path = os.path.join(PROJECTS_DIR, name)

    assert os.path.isdir(project_path)
    assert os.path.isfile(os.path.join(project_path, "config.json"))
    assert os.path.isfile(os.path.join(project_path, "memory.json"))
    assert os.path.isfile(os.path.join(project_path, "features.json"))

    cleanup_project(name)


# ----------------------------
# 2. Invalid project names
# ----------------------------
@pytest.mark.parametrize("name", [
    "invalid name",
    "proj@123",
    "!!!"
])
def test_invalid_project_name(name):
    data = {
        "project_name": name,
        "system_prompt": "Test",
        "stack": "fastapi"
    }

    response = client.post("/project", json=data)

    assert response.status_code == 400


# ----------------------------
# 3. Path traversal
# ----------------------------
@pytest.mark.parametrize("name", [
    "../test",
    "project/abc",
    "project\\abc"
])
def test_path_traversal(name):
    data = {
        "project_name": name,
        "system_prompt": "Test",
        "stack": "fastapi"
    }

    response = client.post("/project", json=data)

    assert response.status_code == 400


# ----------------------------
# 4. Duplicate project
# ----------------------------
def test_project_already_exists():
    name = "duplicate_project"
    project_path = os.path.join(PROJECTS_DIR, name)

    os.makedirs(project_path, exist_ok=True)

    data = {
        "project_name": name,
        "system_prompt": "Test",
        "stack": "fastapi"
    }

    response = client.post("/project", json=data)

    assert response.status_code == 409

    cleanup_project(name)


# ----------------------------
# 5. Missing fields
# ----------------------------
def test_missing_fields():
    response = client.post("/project", json={})

    assert response.status_code == 422


# ----------------------------
# 6. Internal error (FIXED)
# ----------------------------
@patch("routes.project.create_directory")
def test_internal_error(mock_create_dir):
    import uuid
    name = f"error_project_{uuid.uuid4().hex[:6]}"

    mock_create_dir.side_effect = Exception("Disk error")

    data = {
        "project_name": name,
        "system_prompt": "Test",
        "stack": "fastapi"
    }

    response = client.post("/project", json=data)

    assert response.status_code == 500


# ----------------------------
# 7. Config file validation
# ----------------------------
def test_config_file_content():
    name = "config_test"

    data = {
        "project_name": name,
        "system_prompt": "Prompt",
        "stack": "python"
    }

    response = client.post("/project", json=data)
    assert response.status_code == 201

    project_path = os.path.join(PROJECTS_DIR, name)

    with open(os.path.join(project_path, "config.json")) as f:
        config = json.load(f)

    assert config["project_name"] == name
    assert config["system_prompt"] == "Prompt"
    assert config["stack"] == "python"

    cleanup_project(name)