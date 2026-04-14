import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

def generate_from_ollama(prompt: str, model: str = "qwen2.5-coder:7b"):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        }
    )
    
    if response.status_code != 200:
        raise Exception("ollama request failed")
    
    return response.json()["response"]