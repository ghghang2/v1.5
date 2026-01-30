# app/tools/__init__.py
"""Tool registry for the Streamlit + OpenAI integration.

This package contains one module per tool.  The :class:`Tool` data
class defines the public API that the OpenAI chat completions endpoint
expects.  ``TOOLS`` is a list of all available tools and
``get_tools()`` returns the OpenAI‑ready format.

When new tools are added, simply create a new file in this package and
append a :class:`Tool` instance to the ``TOOLS`` list.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List

# Import tool implementations (they live in separate modules)
from .get_stock_price import get_stock_price as _get_stock_price
from .create_file import create_file as _create_file
from .run_command import run_command as _run_command

# --------------------------------------------------------------------------- #
#  Tool dataclass
# --------------------------------------------------------------------------- #
@dataclass
class Tool:
    """Represents a tool that can be called by the OpenAI model."""

    name: str
    description: str
    func: Callable
    schema: Dict[str, Any] = field(init=False)

    def __post_init__(self) -> None:
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
        elif self.name == "run_command":
            self.schema = {
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Shell command to execute, e.g. 'pytest -q'.",
                        },
                    },
                    "required": ["command"],
                }
            }
        else:
            raise NotImplementedError(f"Schema for {self.name} not defined")

# --------------------------------------------------------------------------- #
#  Tool registry
# --------------------------------------------------------------------------- #
TOOLS: List[Tool] = [
    Tool(
        name="get_stock_price",
        description="Get the current stock price for a ticker",
        func=_get_stock_price,
    ),
    Tool(
        name="create_file",
        description="Create a new file at the given path with the supplied content",
        func=_create_file,
    ),
    Tool(
        name="run_command",
        description="Execute a shell command and return its output, return code and stderr",
        func=_run_command,
    ),
]

# --------------------------------------------------------------------------- #
#  Helper – expose OpenAI‑ready tool list
# --------------------------------------------------------------------------- #
def get_tools() -> List[Dict]:
    """Return the list of tools formatted for the OpenAI API."""
    api_tools: List[Dict] = []
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

# --------------------------------------------------------------------------- #
#  Convenience for quick introspection in the REPL
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    print(json.dumps(get_tools(), indent=2))
