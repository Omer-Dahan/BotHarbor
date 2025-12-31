"""Application configuration and paths."""

import os
from pathlib import Path


def get_data_dir() -> Path:
    """Get the application data directory. Creates it if it doesn't exist."""
    # Use the project root's data folder
    # In development: BotHarbor/data
    # Could be changed to %APPDATA%/BotHarbor for installed version
    base_dir = Path(__file__).parent.parent.parent.parent  # src/botharbor/core -> BotHarbor
    data_dir = base_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_database_path() -> Path:
    """Get the SQLite database file path."""
    return get_data_dir() / "botharbor.db"


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
APP_NAME = "BotHarbor"
APP_VERSION = "0.1.0"

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
