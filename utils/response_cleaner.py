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
    code_blocks = re.findall(r"```(?:\w+)?\n(.*?)```", text, re.DOTALL)

    explanation = re.sub(
        r"```(?:\w+)?\n.*?```",
        "",
        text,
        flags=re.DOTALL
    )

    explanation = re.sub(r"^#+.*", "", explanation, flags=re.MULTILINE)

    return {
        "code": [c.strip() for c in code_blocks],
        "explanation": explanation.strip()
    }



def build_claude_style_output(formatted):
    output = ""

    for idx, code in enumerate(formatted["code"], start=1):
        output += f"\n📦 Code Block {idx}\n"
        output += "─" * 60 + "\n"
        output += code.strip() + "\n"
        output += "─" * 60 + "\n"

    if formatted["explanation"]:
        output += "\n🧠 Explanation\n"
        output += "─" * 60 + "\n"
        output += formatted["explanation"].strip() + "\n"

    return output.strip()