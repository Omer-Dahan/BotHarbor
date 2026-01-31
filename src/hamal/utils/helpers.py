"""Utility helper functions."""

import shutil
import sys
from pathlib import Path
from typing import Optional

from hamal.core.config import DEFAULT_ENTRY_PATTERNS, VENV_PYTHON_PATHS


def resource_path(relative_path: str) -> Path:
    """Get absolute path to resource, works for dev and PyInstaller.
    
    In packaged app: resources are relative to executable directory.
    In development: resources are relative to package root (src/hamal).
    
    The PyInstaller spec must bundle resources to match this layout.
    """
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        base_path = Path(sys.executable).parent
    else:
        # Running in development
        base_path = Path(__file__).parent.parent
    return base_path / relative_path


def detect_python_interpreter(project_folder: str) -> str:
    """
    Detect the Python interpreter to use for a project.
    
    Priority:
    1. .venv/Scripts/python.exe
    2. venv/Scripts/python.exe
    3. Returns empty string (UI must warn user to select manually)
    
    Note: We intentionally do NOT fall back to sys.executable because
    in a packaged app, sys.executable points to the app .exe, not Python.
    """
    folder = Path(project_folder)
    
    for venv_path in VENV_PYTHON_PATHS:
        python_path = folder / venv_path
        if python_path.exists():
            return str(python_path.resolve())
    
    # No venv found - return empty, let UI handle warning
    return ""


def detect_entry_file(project_folder: str) -> Optional[str]:
    """
    Auto-detect the entry file for a Python project.
    
    Looks for common patterns: main.py, bot.py, app.py, run.py, __main__.py
    Returns the filename (not full path) or None if not found.
    """
    folder = Path(project_folder)
    
    for pattern in DEFAULT_ENTRY_PATTERNS:
        if (folder / pattern).exists():
            return pattern
    
    return None


def get_python_files(project_folder: str) -> list[str]:
    """Get all Python files in a project folder (non-recursive, root only)."""
    folder = Path(project_folder)
    return [f.name for f in folder.glob("*.py") if f.is_file()]


def format_uptime(seconds: float) -> str:
    """Format seconds into a human-readable uptime string."""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def open_folder_in_explorer(folder_path: str):
    """Open a folder in Windows Explorer."""
    import os
    os.startfile(folder_path)
