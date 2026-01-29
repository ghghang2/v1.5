import json
import os
import pathlib

import pytest

# Import the tool directly from the package
from app.tools import create_file

@pytest.fixture
def unique_filename(tmp_path):
    """
    Return a unique file name that lives under the repository root.
    The file is removed after the test finishes.
    """
    fname = f"tests/tmp_{tmp_path.name}.py"
    yield fname
    # cleanup – the test itself creates/deletes the file, so nothing is required here


def test_create_file_creates_file_and_returns_result(unique_filename):
    """
    Verify that the ``create_file`` tool:
    * writes the given content to the correct path (relative to the repo root)
    * returns a JSON object containing the key ``result``.
    """
    content = "print('hello world')"

    # Call the tool
    result_json = create_file(unique_filename, content)

    # Parse the JSON result
    result = json.loads(result_json)
    assert "result" in result, "Expected a ``result`` key in the JSON response"

    # Verify the file was created with the exact content
    assert pathlib.Path(unique_filename).exists(), "The file was not created"
    with open(unique_filename, encoding="utf-8") as f:
        assert f.read() == content, "File contents do not match the supplied content"

    # Clean up the file so it doesn't affect other tests
    os.remove(unique_filename)


def test_create_file_prevents_directory_traversal():
    """
    The tool must reject attempts to write outside the repository root.
    It should return a JSON object containing an ``error`` key.
    """
    # Path that tries to escape the repo root
    bad_path = "../../outside.txt"
    content = "secret"

    result_json = create_file(bad_path, content)
    result = json.loads(result_json)

    assert "error" in result, "Expected an ``error`` key for a path traversal attempt"
    # Ensure the file was not created
    assert not pathlib.Path(bad_path).exists(), "File was created outside the repo root"
