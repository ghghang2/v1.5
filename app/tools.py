# app/tools.py
"""
Tool definitions for the Streamlit + OpenAI integration.

This module now contains:
1. `get_stock_price` – demo stock‑price lookup.
2. `create_file`   – add a new file to the repo.
"""

from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass, field
from typing import Callable, Dict, List

# --------------------------------------------------------------------------- #
#  Helper – safe path resolution
# --------------------------------------------------------------------------- #
def _safe_resolve(repo_root: pathlib.Path, rel_path: str) -> pathlib.Path:
    """
    Resolve *rel_path* against *repo_root* and ensure the result
    does not escape the repository root (prevents directory traversal).
    """
    target = (repo_root / rel_path).resolve()
    if not str(target).startswith(str(repo_root)):
        raise ValueError("Path escapes repository root")
    return target


# --------------------------------------------------------------------------- #
#  Tool dataclass
# --------------------------------------------------------------------------- #
@dataclass
class Tool:
    name: str
    description: str
    func: Callable
    schema: Dict[str, any] = field(init=False)

    def __post_init__(self):
        # Define the JSON schema for each supported tool.
        if self.name == "get_stock_price":
            self.schema = {
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticker": {
                            "type": "string",
                            "description": "Stock symbol, e.g. AAPL",
                        },
                    },
                    "required": ["ticker"],
                }
            }
        elif self.name == "create_file":
            self.schema = {
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Relative path of the new file (e.g. 'app/new_module.py')",
                        },
                        "content": {
                            "type": "string",
                            "description": "File contents as a plain string.",
                        },
                    },
                    "required": ["path", "content"],
                }
            }
        else:
            raise NotImplementedError(f"Schema for {self.name} not defined")


# --------------------------------------------------------------------------- #
#  Existing tool – get_stock_price
# --------------------------------------------------------------------------- #
def get_stock_price(ticker: str) -> str:
    """
    Demo function that returns a mock stock price.
    The real implementation can query a live API.
    """
    sample_data = {"AAPL": 24, "GOOGL": 178.20, "NVDA": 580.12}
    price = sample_data.get(ticker.upper(), "unknown")
    return json.dumps({"ticker": ticker.upper(), "price": price})


# --------------------------------------------------------------------------- #
#  New tool – create_file
# --------------------------------------------------------------------------- #
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
#  Register the tools
# --------------------------------------------------------------------------- #
TOOLS: List[Tool] = [
    Tool(
        name="get_stock_price",
        description="Get the current stock price for a ticker",
        func=get_stock_price,
    ),
    Tool(
        name="create_file",
        description="Create a new file at the given path with the supplied content",
        func=create_file,
    ),
]


# --------------------------------------------------------------------------- #
#  Helper – expose OpenAI‑ready tool list
# --------------------------------------------------------------------------- #
def get_tools() -> List[Dict]:
    """
    Return a list of tool definitions formatted for the OpenAI API.
    Each element includes the required `"type": "function"` wrapper.
    """
    api_tools = []
    for t in TOOLS:
        api_tools.append(
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.schema["parameters"],
                },
            }
        )
    return api_tools