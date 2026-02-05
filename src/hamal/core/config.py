"""Application configuration and paths."""

import os
from pathlib import Path


def get_data_dir() -> Path:
    """Get the application data directory. Creates it if it doesn't exist.
    
    Uses %LOCALAPPDATA%\\HAMAL\\ on Windows for installer compatibility.
    This keeps user data separate from Program Files (read-only).
    """
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        data_dir = Path(local_app_data) / "HAMAL"
    else:
        # Fallback for non-Windows or missing env var
        data_dir = Path.home() / ".hamal"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_database_path() -> Path:
    """Get the SQLite database file path."""
    return get_data_dir() / "hamal.db"


def get_logs_dir() -> Path:
    """Get the logs directory."""
    logs_dir = get_data_dir() / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


def get_project_logs_dir(project_id: int) -> Path:
    """Get the logs directory for a specific project."""
    project_logs_dir = get_logs_dir() / str(project_id)
    project_logs_dir.mkdir(parents=True, exist_ok=True)
    return project_logs_dir


# Application constants
APP_NAME = "H.A.M.A.L"
APP_VERSION = "0.1.1"

# Default entry file patterns to look for when adding a project
DEFAULT_ENTRY_PATTERNS = [
    "main.py",
    "bot.py",
    "app.py",
    "run.py",
    "__main__.py",
]

# Venv detection paths (Windows)
VENV_PYTHON_PATHS = [
    ".venv/Scripts/python.exe",
    "venv/Scripts/python.exe",
]
