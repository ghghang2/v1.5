import json
import os
import sys
import subprocess
from pathlib import Path

# Ensure the repository root is on sys.path for imports
sys.path.append(os.path.abspath("."))

from app.tools.apply_patch import func as apply_patch


def test_apply_patch_tool_success():
    """Test that the apply_patch tool can apply a simple patch.

    The test creates a file in the repository root, writes a patch that
    changes its content, and ensures that the file content is updated.
    """
    repo_root = Path(__file__).resolve().parents[1]
    test_file = repo_root / "test_file.txt"
    # Make sure the file starts with known content
    test_file.write_text("old content\n")

    # Create a unified diff patch that changes the line
    patch_text = (
        "--- a/test_file.txt\n"
        "+++ b/test_file.txt\n"
        "@@ -1 +1 @@\n"
        "-old content\n"
        "+new content\n"
    )

    result_json = apply_patch("test_file.txt", patch_text)
    result = json.loads(result_json)
    assert "result" in result, f"Tool returned error: {result.get('error')}"
    # Verify that the file content has been updated
    assert test_file.read_text() == "new content\n"


def test_apply_patch_tool_error():
    """Test that the tool reports an error when git apply fails.

    The patch references a non-existent file, which should cause the
    ``git apply`` command to fail.
    """
    repo_root = Path(__file__).resolve().parents[1]
    # Ensure the repository root has a git repository
    subprocess.run(["git", "init", "-q"], cwd=str(repo_root), check=True)
    # Patch that refers to a file that does not exist
    patch_text = (
        "--- a/nonexistent.txt\n"
        "+++ b/nonexistent.txt\n"
        "@@ -1 +1 @@\n"
        "-old\n"
        "+new\n"
    )
    result_json = apply_patch("nonexistent.txt", patch_text)
    result = json.loads(result_json)
    assert "error" in result
