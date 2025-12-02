import os
from typing import Dict


def write_file_tree(file_tree: Dict[str, str], root: str) -> None:
    os.makedirs(root, exist_ok=True)

    for path, content in file_tree.items():
        full_path = os.path.join(root, path)

        # If the path ends with "/" or content is None, it's a directory
        if path.endswith("/") or content is None:
            os.makedirs(full_path, exist_ok=True)
            continue

        # Ensure parent directory exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # Write file normally
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
