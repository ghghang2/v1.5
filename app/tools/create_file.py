# app/tools/create_file.py
"""
Tool that creates a new file under the repository root.

The function validates the target path so that it cannot escape the
repository root (prevents directory traversal).  It creates any missing
parent directories, writes the supplied content, and returns a JSON
string containing either a `result` key (success) or an `error` key
(failure).

The JSON format is compatible with the OpenAI function‑calling schema
used by the chat UI.
"""

import json
import pathlib
from typing import Dict


def _safe_resolve(repo_root: pathlib.Path, rel_path: str) -> pathlib.Path:
    """
    Resolve *rel_path* against *repo_root* and ensure the result
    does not escape the repository root (prevents directory traversal).
    """
    target = (repo_root / rel_path).resolve()
    if not str(target).startswith(str(repo_root)):
        raise ValueError("Path escapes repository root")
    return target


def create_file(path: str, content: str) -> str:
    """
    Create a new file at *path* (relative to the repo root) with the supplied
    *content*.  Returns a JSON string containing either a `result` or an
    `error` key.
    """
    try:
        repo_root = pathlib.Path(__file__).resolve().parent.parent
        target = _safe_resolve(repo_root, path)

        # Make sure the parent directory exists
        target.parent.mkdir(parents=True, exist_ok=True)

        # Write the file
        target.write_text(content, encoding="utf-8")

        return json.dumps({"result": f"File created: {path}"})
    except Exception as exc:
        return json.dumps({"error": str(exc)})

# --------------------------------------------------------------------------- #
#  Export the tool as part of the public API
# --------------------------------------------------------------------------- #
__all__ = ["create_file"]
