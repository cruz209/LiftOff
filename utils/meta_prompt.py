#
# from typing import Dict
#
#
# def build_meta_prompt(user_prompt: str, metadata: dict) -> str:
#     """
#     Build the meta-prompt LiftOff sends to the model.
#     This ALWAYS expands natural language into a full project blueprint
#     before generating code. No special-case hacks.
#     """
#
#     return f"""
# You are LiftOff, a project scaffolding engine.
#
# Your job:
# 1. Take the user’s short natural language request.
# 2. Expand it into a detailed, explicit blueprint.
# 3. Then generate a complete project file tree based on that blueprint.
#
# You MUST follow this pipeline:
#
# ----------------------------------------
# ### STEP 1 — Interpret & Infer
# Expand the user's vague request into a full specification:
# - Identify the project type (web app, CLI tool, agent, library, API service, etc.)
# - Identify major components needed.
# - Identify subcomponents and utilities.
# - Infer missing requirements.
# - Infer reasonable defaults.
# - Select appropriate libraries.
# - Select folder structure.
#
# Represent this as a structured JSON-like plan INSIDE YOUR REASONING (NOT in the output).
#
# ----------------------------------------
# ### STEP 2 — Output ONLY a File Tree
# You MUST output ONLY a JSON object where:
# - keys = file paths
# - values = full file contents
# - NO markdown, NO backticks, NO commentary
#
# The generated code MUST:
# - include runnable boilerplate
# - include all core logic (no TODOs)
# - be consistent with the inferred architecture
# - follow the best practices of the chosen stack
#
# ----------------------------------------
#
# ### GLOBAL RULES
# - If the user gives an under-specified request, infer details logically.
# - All files must be complete enough to run.
# - Avoid placeholders. Implement real logic.
# - Use the simplest viable libraries.
# - If an LLM is needed, default to OpenAI (client = OpenAI()).
#
# ----------------------------------------
#
# ### USER REQUEST:
# {user_prompt}
# """
#
from typing import Dict

def build_meta_prompt(user_prompt: str, metadata: Dict) -> str:
    """
    Universal LiftOff meta-prompt:
    - Always expands vague user instructions into a full project blueprint.
    - Always generates a complete runnable project.
    - Always uses an environment-loaded OpenAI client via config.py.
    """

    framework = metadata.get("framework") or "Python"
    app_type = metadata.get("app_type") or "application"

    return f"""
You are LiftOff, a project scaffolding engine.

Your job has two stages:

------------------------------------------------------------
### STAGE 1 — ARCHITECTURE EXPANSION (internal reasoning)
Interpret the user's short natural-language description and expand it into a
fully specified project blueprint. Infer:
- project type ({app_type},, CLI, API service, agent, library, etc.)
- folder structure
- modules and submodules
- utilities needed
- data flow
- routes/endpoints (if any)
- dependencies
- expected behavior
- any missing details

You must fill in missing details logically.
This planning stays INTERNAL — do NOT output it.

------------------------------------------------------------
### STAGE 2 — OUTPUT: PROJECT FILE TREE (JSON ONLY)
Output ONLY a JSON object where:
- Keys = file paths
- Values = COMPLETE file contents
- No comments outside code
- No markdown
- No backticks
- All code must be runnable

------------------------------------------------------------
### GLOBAL CODE RULES
- All files must be complete and runnable without modification.
- Avoid stubs, TODOs, placeholders, or fake functions.
- Use simplest, cleanest idioms for the chosen framework ({framework}).
- If LLMs are used, ALWAYS use OpenAI's Python client.
- ALL projects that use LLMs MUST include a shared config.py file:

    import os
    from openai import OpenAI

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY environment variable is not set.")
    client = OpenAI(api_key=OPENAI_API_KEY)
- When generating Python code that calls the OpenAI API, always use the modern 2025+ style:

from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

Use:
    client.chat.completions.create(...)
    model="gpt-4o-mini" by default

Never use:
    openai.Completion.create
    text-davinci-003
    legacy endpoints

- Any file that uses LLMs MUST import the shared client using:
    from config import client

- Never hardcode API keys.
- Never require user interaction during runtime.
- For web apps: include basic templates and minimal CSS.
- For CLIs: include entry points and argparse handling.
- For libraries: include __init__.py

------------------------------------------------------------
### USER REQUEST:
{user_prompt}
"""
