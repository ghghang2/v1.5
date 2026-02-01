# app/tools/apply_patch.py
"""Tool to apply a unified diff patch to the repository.

The function expects a relative path to the target file (or directory) and
raw patch text.  It writes the patch to a temporary file and uses
``git apply`` to apply it.  The return value is a JSON string that
contains either a ``result`` key with a human‑readable message or an
``error`` key if the operation fails.

The module exports ``func``, ``name`` and ``description`` attributes so
that :mod:`app.tools.__init__` can discover it.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import tempfile
from pathlib import Path
from typing import Dict

# ---------------------------------------------------------------------------
# Public attributes for tool discovery
# ---------------------------------------------------------------------------
name = "apply_patch"
description = "Apply a unified diff patch to the repository using git apply."

# ---------------------------------------------------------------------------
# The actual implementation
# ---------------------------------------------------------------------------

def _apply_patch(path: str, patch_text: str) -> str:
    """Apply *patch_text* to the file or directory specified by *path*.

    Parameters
    ----------
    path:
        File or directory path relative to the repository root.
    patch_text:
        Unified diff string.

    Returns
    -------
    str
        JSON string with either ``result`` or ``error``.
    """
    try:
        repo_root = Path(__file__).resolve().parents[3]
        target = (repo_root / path).resolve()
        if not str(target).startswith(str(repo_root)):
            raise ValueError("Path escapes repository root")

        # Write patch to temp file
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".patch") as tmp:
            tmp.write(patch_text)
            tmp_path = Path(tmp.name)

        # Run git apply
        result = subprocess.run(
            ["git", "apply", str(tmp_path)],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        tmp_path.unlink(missing_ok=True)

        if result.returncode != 0:
            return json.dumps({"error": f"git apply failed: {result.stderr.strip()}"})
        return json.dumps({"result": "Patch applied successfully"})
    except Exception as exc:  # pragma: no cover
        return json.dumps({"error": str(exc)})

# Exported callable for discovery
func = _apply_patch
__all__ = ["func", "name", "description"]
