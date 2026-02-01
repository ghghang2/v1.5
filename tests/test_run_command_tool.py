import json
import os
import sys
from pathlib import Path

# Ensure the repository root is on sys.path for imports
sys.path.append(os.path.abspath("."))

from app.tools.run_command import func as run_command


def test_run_command_basic():
    """Verify that a simple command returns stdout, stderr and exit code."""
    result_json = run_command("echo hello")
    result = json.loads(result_json)
    assert "stdout" in result and "stderr" in result and "exit_code" in result
    assert result["stdout"].strip() == "hello"
    assert result["stderr"].strip() == ""
    assert result["exit_code"] == 0


def test_run_command_with_cwd():
    """Verify that the cwd argument correctly changes the working directory."""
    # Create a temporary subdirectory inside the repository root
    cwd_dir = Path(__file__).parent / "tmp_subdir"
    cwd_dir.mkdir(exist_ok=True)
    # Run a command that prints the working directory
    cwd_rel = str(cwd_dir.relative_to(Path(__file__).resolve().parents[1]))
    result_json = run_command("pwd", cwd=cwd_rel)
    result = json.loads(result_json)
    assert result["exit_code"] == 0
    # The output should be the absolute path to the subdir
    expected_path = str(cwd_dir)
    assert result["stdout"].strip() == expected_path


def test_run_command_error():
    """Verify that a non-existent command returns a non-zero exit code."""
    result_json = run_command("this-command-does-not-exist")
    result = json.loads(result_json)
    assert "stdout" in result
    assert "stderr" in result
    assert "exit_code" in result
    assert result["exit_code"] != 0
