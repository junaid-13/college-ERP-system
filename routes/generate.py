from fastapi import APIRouter, HTTPException, status, Query
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
import os
import re
from functools import lru_cache
import asyncio
import logging
import time

from services.ollama_client import generate_from_ollama
from services.prompt_builder import build_prompt
from services.memory_manager import load_memory, update_memory
from services.context_builder import get_relevant_files, format_code_context
from services.feature_manager import load_features
from utils.file_handler import read_json
from utils.response_cleaner import clean_response, format_llm_output, build_claude_style_output


router = APIRouter()
logger = logging.getLogger(__name__)

PROJECTS_DIR = os.path.abspath("projects")


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
        clean_path = os.path.normpath(f)

        if clean_path.startswith("..") or os.path.isabs(clean_path):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file path: {f}"
            )
        safe_files.append(f)

    return safe_files


class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    files: list[str] = Field(default_factory=list)


@lru_cache(maxsize=100)
def get_cached_config(project_path: str):
    return read_json(os.path.join(project_path, "config.json"))


@lru_cache(maxsize=100)
def get_cached_features(project_name: str):
    return load_features(project_name)


@router.post("/generate/{project_name}")
async def generate(
    project_name: str,
    body: GenerateRequest,
    pretty: bool = Query(True)
):
    project_name = validate_project_name(project_name)
    project_path = os.path.join(PROJECTS_DIR, project_name)

    if not os.path.isdir(project_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found."
        )

    try:
        config = get_cached_config(project_path)
        if not config:
            raise HTTPException(500, "Invalid or missing config.json")

        memory = load_memory(project_name)
        if not memory:
            raise HTTPException(500, "Invalid or missing memory.json")

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

        start = time.time()
        logger.info(f"[project={project_name}] LLM call started")

        raw_result = await asyncio.wait_for(
            asyncio.to_thread(generate_from_ollama, final_prompt),
            timeout=3600  
        )

        end = time.time()
        logger.info(f"[project={project_name}] LLM finished in {end - start:.2f}s")

        if not raw_result:
            raise HTTPException(500, "Empty response from generation service")

        logger.info(f"[project={project_name}] Raw LLM output received")

        cleaned = clean_response(raw_result)
        formatted = format_llm_output(cleaned)

        if not isinstance(formatted, dict):
            raise HTTPException(500, "Invalid formatted output")

        formatted.setdefault("code", [])
        formatted.setdefault("explanation", "")

        pretty_output = build_claude_style_output(formatted)

        try:
            updated_memory = update_memory(
                project_name,
                memory,
                body.prompt,
                cleaned
            )
        except Exception as e:
            logger.error(f"[project={project_name}] Memory update failed: {repr(e)}")
            updated_memory = memory

    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="LLM request timed out"
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.exception(f"[project={project_name}] Unexpected generation failure: {repr(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Generation failed: {repr(e)}"
        )

    if pretty:
        return PlainTextResponse(pretty_output)

    return {
        "code": formatted["code"],
        "explanation": formatted["explanation"],
        "memory": updated_memory,
        "used_files": [
            f[0] for f in files
            if isinstance(f, (list, tuple)) and len(f) > 0
        ]
    }