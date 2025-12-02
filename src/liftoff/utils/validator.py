import ast
import os
import re
from typing import Dict, List


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

IMPORT_RE = re.compile(r"from\s+([\w\.]+)\s+import\s+([\w\*\,\s]+)|import\s+([\w\.]+)")
ROUTE_RE = re.compile(r"@app\.route\(['\"](.*?)['\"]")
FETCH_RE = re.compile(r"\$.post\(['\"](.*?)['\"]")

OPENAI_BAD_PATTERNS = [
    r"openai\.Completion",
    r"text-davinci",
    r"openai\.ChatCompletion",
]

REQUIRED_FILES_FOR_LLM = ["config.py"]


# ------------------------------------------------------------
# Validator Entry Point
# ------------------------------------------------------------

def validate_file_tree(file_tree: Dict[str, str]) -> List[str]:
    issues = []

    # ------------------------------
    # (1) Check file paths for sanity
    # ------------------------------
    for path in file_tree:
        if not isinstance(path, str) or path.strip() == "":
            issues.append(f"Invalid file path key: {path!r}")
        if path.startswith("/") or "\\" in path:
            issues.append(f"Bad path formatting: {path}")

    # ------------------------------
    # (2) Check imports
    # ------------------------------
    issues.extend(_check_imports(file_tree))

    # ------------------------------
    # (3) Check syntax for Python files
    # ------------------------------
    issues.extend(_check_python_syntax(file_tree))

    # ------------------------------
    # (4) Check directory consistency
    # ------------------------------
    issues.extend(_check_directories(file_tree))

    # ------------------------------
    # (5) Check JS/backend contract (upload/ask)
    # ------------------------------
    issues.extend(_check_js_contract(file_tree))

    # ------------------------------
    # (6) Check OpenAI API usage correctness
    # ------------------------------
    issues.extend(_check_openai_usage(file_tree))

    # ------------------------------
    # (7) Ensure LLM projects include config.py
    # ------------------------------
    issues.extend(_check_llm_config_presence(file_tree))

    return issues


# ------------------------------------------------------------
# IMPORT CHECKS
# ------------------------------------------------------------

def _check_imports(file_tree: Dict[str, str]) -> List[str]:
    issues = []
    python_files = {p: c for p, c in file_tree.items() if p.endswith(".py")}

    module_names = {
        os.path.splitext(p)[0].replace("/", "."): p
        for p in file_tree.keys()
    }

    for path, content in python_files.items():
        for match in IMPORT_RE.finditer(content):
            module = match.group(1) or match.group(3)
            if not module:
                continue

            direct_file = module.replace(".", "/") + ".py"
            if direct_file not in file_tree:
                # allow external modules
                if module.split(".")[0] in ("os", "sys", "json", "flask", "openai", "typing"):
                    continue
                issues.append(f"[IMPORT] {path} imports missing file '{direct_file}'")

    return issues


# ------------------------------------------------------------
# PYTHON SYNTAX CHECKS
# ------------------------------------------------------------

def _check_python_syntax(file_tree: Dict[str, str]) -> List[str]:
    issues = []
    for path, content in file_tree.items():
        if not path.endswith(".py"):
            continue
        try:
            ast.parse(content)
        except SyntaxError as e:
            issues.append(f"[SYNTAX] {path} contains invalid Python: {e}")
    return issues


# ------------------------------------------------------------
# DIRECTORY CHECKS
# ------------------------------------------------------------

def _check_directories(file_tree: Dict[str, str]) -> List[str]:
    issues = []
    for path, content in file_tree.items():
        if path.endswith("/") and content is not None:
            issues.append(f"[DIR] Directory '{path}' should have content=None")
        if "/" in path and not any(k.startswith(os.path.dirname(path)) for k in file_tree):
            # Parent directory missing
            parent = os.path.dirname(path)
            if parent not in ("", ".") and parent + "/" not in file_tree:
                issues.append(f"[DIR] Missing parent directory for {path}: expected '{parent}/'")
    return issues


# ------------------------------------------------------------
# JS/ROUTE CONTRACT CHECKS
# ------------------------------------------------------------

def _check_js_contract(file_tree: Dict[str, str]) -> List[str]:
    issues = []
    frontend_routes = set()
    backend_routes = set()

    # Find backend Flask routes
    for path, content in file_tree.items():
        if path.endswith(".py"):
            for m in ROUTE_RE.finditer(content):
                backend_routes.add(m.group(1))

    # Find frontend jQuery $.post calls
    for path, content in file_tree.items():
        if path.endswith(".html") or path.endswith(".js"):
            for m in FETCH_RE.finditer(content):
                frontend_routes.add(m.group(1))

    # Compare
    for route in frontend_routes:
        if route not in backend_routes:
            issues.append(f"[ROUTE] Frontend calls '{route}' but backend route missing.")

    return issues


# ------------------------------------------------------------
# OPENAI API SAFETY CHECK
# ------------------------------------------------------------

def _check_openai_usage(file_tree: Dict[str, str]) -> List[str]:
    issues = []
    for path, content in file_tree.items():
        if not path.endswith(".py"):
            continue
        for pattern in OPENAI_BAD_PATTERNS:
            if re.search(pattern, content):
                issues.append(f"[OPENAI] {path} uses deprecated OpenAI pattern: {pattern}")
    return issues


# ------------------------------------------------------------
# CONFIG.PY PRESENCE CHECK
# ------------------------------------------------------------

def _check_llm_config_presence(file_tree: Dict[str, str]) -> List[str]:
    issues = []
    llm_used = False

    for path, content in file_tree.items():
        if path.endswith(".py") and "OpenAI(" in content:
            llm_used = True

    if llm_used and "config.py" not in file_tree:
        issues.append("[CONFIG] Missing required config.py for OpenAI client.")

    return issues
