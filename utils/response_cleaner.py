import re


def clean_response(text: str) -> str:
    if not text:
        return ""

    text = text.strip()

    text = re.sub(
        r"^(here (is|are)|sure|of course).*?\n",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = text.replace("\r\n", "\n").replace("\r", "\n")

    text = re.sub(r"\n{3,}", "\n\n", text)

    return text


def format_llm_output(text: str):
    code_blocks = re.findall(r"```(?:\w+)?\s*([\s\S]*?)```", text)

    explanation = re.sub(
        r"```(?:\w+)?\s*.*?```",
        "",
        text,
        flags=re.DOTALL
    )

    explanation = re.sub(
        r"^#{1,3}\s*(Code|Explanation).*",
        "",
        explanation,
        flags=re.IGNORECASE | re.MULTILINE
    )

    # Fallback if no code found
    if not code_blocks:
        return {
            "code": [],
            "explanation": text.strip()
        }

    return {
        "code": [c.strip() for c in code_blocks],
        "explanation": explanation.strip()
    }


def build_claude_style_output(formatted):
    lines = []

    for idx, code in enumerate(formatted.get("code", []), start=1):
        lines.append(f"📦 Code Block {idx}")
        lines.append("─" * 60)
        lines.append(code.strip())
        lines.append("─" * 60)
        lines.append("")

    if formatted.get("explanation"):
        lines.append("🧠 Explanation")
        lines.append("─" * 60)
        lines.append(formatted["explanation"].strip())

    return "\n".join(lines).strip()