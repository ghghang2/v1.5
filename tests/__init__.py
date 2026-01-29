# tests/__init__.py
"""
Make the repository root importable during test collection.
"""

import pathlib
import sys

# Path to the repository root (the directory that contains `app/`).
ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent

# Ensure the root is first in sys.path.
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
