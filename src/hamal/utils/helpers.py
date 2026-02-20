"""Utility helper functions."""

import os
import sys
from pathlib import Path
from typing import Optional

from hamal.core.project_scanner import ProjectScanner, get_all_script_files


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
    
    Uses smart recursive scanning to find virtual environments.
    Returns empty string if no venv found (UI must warn user to select manually).
    """
    scanner = ProjectScanner()
    result = scanner.scan(project_folder)
    return result.interpreter or ""


def detect_entry_file(project_folder: str) -> Optional[str]:
    """
    Auto-detect the entry file for a project.
    
    Uses smart recursive scanning to find entrypoints in subdirectories.
    Returns the relative path from project root, or None if not found.
    """
    scanner = ProjectScanner()
    result = scanner.scan(project_folder)
    return result.entrypoint


def get_python_files(project_folder: str) -> list[str]:
    """Get all script files in a project folder (recursive, up to 3 levels deep)."""
    return get_all_script_files(project_folder, max_depth=3)


def format_uptime(seconds: float) -> str:
    """Format seconds into a human-readable uptime string."""
    if seconds < 60:
        return f"{int(seconds)}s"
    if seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{hours}h {minutes}m"


def open_folder_in_explorer(folder_path: str):
    """Open a folder in Windows Explorer."""
    os.startfile(folder_path)
