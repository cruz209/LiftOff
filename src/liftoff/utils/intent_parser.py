import re
from typing import Dict

ACADEMIC_KEYWORDS = [
    "homework", "assignment", "essay", "problem set", "lab",
    "midterm", "final", "exam", "quiz", "due", "worksheet"
]

def is_academic_misuse(prompt: str) -> bool:
    p = prompt.lower()
    return any(term in p for term in ACADEMIC_KEYWORDS)


def parse_intent(prompt: str) -> Dict:
    """Lightweight v0 intent parser. Fast, regex-based, no ML."""
    p = prompt.lower()

    # 1. Academic misuse detection
    if is_academic_misuse(p):
        return {"blocked": True}

    # 2. Framework detection
    if "flask" in p:
        framework = "Flask"
    elif "fastapi" in p:
        framework = "FastAPI"
    elif "streamlit" in p:
        framework = "Streamlit"
    else:
        framework = "Flask"  # sensible default

    # 3. App type detection
    if "rag" in p or "retrieval" in p:
        app_type = "RAG app"
    elif "chat" in p:
        app_type = "chatbot"
    elif "api" in p:
        app_type = "API service"
    elif "dashboard" in p:
        app_type = "dashboard"
    else:
        app_type = "general_app"

    # 4. Project name
    project_name = f"{framework.lower()}_{app_type.replace(' ', '_')}"

    return {
        "blocked": False,
        "framework": framework,
        "app_type": app_type,
        "project_name": project_name,
    }
