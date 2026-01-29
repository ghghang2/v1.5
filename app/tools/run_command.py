# app/tools/run_command.py
"""
Tool that executes a shell command and returns its output.

The tool is safe for the repository root – it does not allow changing
directories or writing files outside the repo.  The command is run
through a subprocess with `shell=True` so that the user can use shell
syntax (e.g. pipes, redirection).  The tool captures stdout, stderr and
the exit code, and returns a JSON string that the model can consume.

The function is intentionally minimal to avoid accidental side‑effects.
"""

import json
import subprocess
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


def run_command(command: str, cwd: str | None = None) -> str:
    """
    Execute *command* in the repository root (or a sub‑directory if
    *cwd* is provided) and return a JSON string with:
        * stdout
        * stderr
        * exit_code
    Any exception is converted to an error JSON.
    """
    try:
        repo_root = pathlib.Path(__file__).resolve().parent.parent
        if cwd:
            target_dir = _safe_resolve(repo_root, cwd)
        else:
            target_dir = repo_root

        # Run the command
        proc = subprocess.run(
            command,
            shell=True,
            cwd=str(target_dir),
            capture_output=True,
            text=True,
        )
        result: Dict[str, str | int] = {
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "exit_code": proc.returncode,
        }
        return json.dumps(result)

    except Exception as exc:
        # Return a JSON with an error key
        return json.dumps({"error": str(exc)})

# --------------------------------------------------------------------------- #
#  Export the tool as part of the public API
# --------------------------------------------------------------------------- #
__all__ = ["run_command"]
