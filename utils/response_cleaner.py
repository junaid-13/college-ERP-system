def clean_response(text: str):
    # Remove leading/trailing garbage
    text = text.strip()

    # Optional: remove unwanted prefixes
    if text.lower().startswith("here is"):
        text = text.split("\n", 1)[-1]

    return text