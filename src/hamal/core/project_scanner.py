"""Smart project scanning for automatic entrypoint and interpreter detection."""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


# Entry file patterns by priority (checked in order)
ENTRY_PATTERNS = [
    # Python - most common first
    "main.py",
    "bot.py", 
    "app.py",
    "run.py",
    "__main__.py",
    "index.py",
    "server.py",
    "cli.py",
    # JavaScript/Node.js
    "index.js",
    "app.js",
    "server.js",
    "main.js",
    "bot.js",
    # Go
    "main.go",
    # PHP
    "index.php",
    "app.php",
    # Ruby
    "main.rb",
    "app.rb",
]

# Folders to skip during recursive search
SKIP_FOLDERS = {
    ".git",
    ".venv",
    "venv",
    "env",
    ".env",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "dist",
    "build",
    ".tox",
    "eggs",
    "*.egg-info",
}

# Virtual environment paths to check (Windows)
VENV_INTERPRETER_PATHS = [
    ".venv/Scripts/python.exe",
    "venv/Scripts/python.exe",
    "env/Scripts/python.exe",
    ".env/Scripts/python.exe",
]


@dataclass
class ScanResult:
    """Result of project scanning."""
    entrypoint: Optional[str] = None  # Relative path from project root
    interpreter: Optional[str] = None  # Absolute path to interpreter
    language: Optional[str] = None  # Detected language
    confidence: float = 0.0  # 0.0 to 1.0


class ProjectScanner:
    """
    Smart project scanner that recursively finds entrypoints and interpreters.
    
    Detection priority:
    1. Config files (package.json, pyproject.toml)
    2. Root folder patterns
    3. Recursive search (up to max_depth)
    """
    
    def __init__(self, max_depth: int = 5):
        self.max_depth = max_depth
    
    def scan(self, folder: str) -> ScanResult:
        """
        Scan a project folder and detect entrypoint + interpreter.
        
        Args:
            folder: Absolute path to project folder
            
        Returns:
            ScanResult with detected values
        """
        folder_path = Path(folder)
        result = ScanResult()
        
        if not folder_path.exists():
            logger.warning(f"[Scanner] Folder does not exist: {folder}")
            return result
        
        logger.info(f"[Scanner] Scanning: {folder}")
        
        # Step 1: Try to detect from config files
        config_result = self._scan_config_files(folder_path)
        if config_result.entrypoint:
            logger.info(f"[Scanner] Found entrypoint from config: {config_result.entrypoint}")
            result = config_result
        
        # Step 2: Check root folder for common patterns
        if not result.entrypoint:
            root_entry = self._find_entry_in_folder(folder_path)
            if root_entry:
                result.entrypoint = root_entry
                result.confidence = 0.9
                logger.info(f"[Scanner] Found entrypoint in root: {root_entry}")
        
        # Step 3: Recursive search
        if not result.entrypoint:
            recursive_entry = self._find_entry_recursive(folder_path)
            if recursive_entry:
                result.entrypoint = recursive_entry
                result.confidence = 0.7
                logger.info(f"[Scanner] Found entrypoint recursively: {recursive_entry}")
        
        # Step 4: Find interpreter
        interpreter = self._find_interpreter(folder_path)
        if interpreter:
            result.interpreter = interpreter
            logger.info(f"[Scanner] Found interpreter: {interpreter}")
        
        # Detect language from entrypoint
        if result.entrypoint:
            result.language = self._detect_language(result.entrypoint)
        
        return result
    
    def _scan_config_files(self, folder: Path) -> ScanResult:
        """Check config files for entrypoint definitions."""
        result = ScanResult()
        
        # Check package.json (Node.js)
        package_json = folder / "package.json"
        if package_json.exists():
            try:
                with open(package_json, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    main = data.get("main")
                    if main:
                        result.entrypoint = main
                        result.language = "javascript"
                        result.confidence = 1.0
                        return result
            except Exception as e:
                logger.debug(f"[Scanner] Error reading package.json: {e}")
        
        # Check pyproject.toml (Python)
        pyproject = folder / "pyproject.toml"
        if pyproject.exists():
            try:
                content = pyproject.read_text(encoding="utf-8")
                # Simple parsing - look for scripts section
                if "[project.scripts]" in content or "[tool.poetry.scripts]" in content:
                    # Has scripts defined, but we'd need toml parser to extract
                    # For now, just note it's a Python project
                    result.language = "python"
            except Exception as e:
                logger.debug(f"[Scanner] Error reading pyproject.toml: {e}")
        
        return result
    
    def _find_entry_in_folder(self, folder: Path) -> Optional[str]:
        """Find entry file in a specific folder (non-recursive)."""
        for pattern in ENTRY_PATTERNS:
            entry_path = folder / pattern
            if entry_path.exists() and entry_path.is_file():
                return pattern
        return None
    
    def _find_entry_recursive(self, root: Path, current_depth: int = 0) -> Optional[str]:
        """Recursively search for entry files."""
        if current_depth >= self.max_depth:
            return None
        
        try:
            for item in root.iterdir():
                if item.is_dir():
                    # Skip excluded folders
                    if item.name in SKIP_FOLDERS:
                        continue
                    if any(item.name.endswith(skip.replace("*", "")) for skip in SKIP_FOLDERS if "*" in skip):
                        continue
                    
                    # Check this subfolder
                    entry = self._find_entry_in_folder(item)
                    if entry:
                        # Return relative path from project root
                        relative = item.relative_to(root.parent if current_depth == 0 else root)
                        return str(Path(item.name) / entry)
                    
                    # Go deeper
                    deeper = self._find_entry_recursive(item, current_depth + 1)
                    if deeper:
                        return str(Path(item.name) / deeper)
        except PermissionError:
            pass
        
        return None
    
    def _find_interpreter(self, folder: Path) -> Optional[str]:
        """Find Python interpreter, checking recursively for venvs."""
        # First check standard locations in project root
        for venv_path in VENV_INTERPRETER_PATHS:
            interpreter = folder / venv_path
            if interpreter.exists():
                return str(interpreter.resolve())
        
        # Recursive search for venv in subdirectories
        return self._find_interpreter_recursive(folder, 0)
    
    def _find_interpreter_recursive(self, folder: Path, depth: int) -> Optional[str]:
        """Recursively search for virtual environments."""
        if depth >= self.max_depth:
            return None
        
        try:
            for item in folder.iterdir():
                if item.is_dir():
                    # Skip non-venv folders
                    if item.name in SKIP_FOLDERS and item.name not in {".venv", "venv", "env", ".env"}:
                        continue
                    
                    # Check if this folder is a venv
                    python_exe = item / "Scripts" / "python.exe"
                    if python_exe.exists():
                        return str(python_exe.resolve())
                    
                    # Check subfolders (but not too deep)
                    if item.name not in {".git", "node_modules", "__pycache__"}:
                        result = self._find_interpreter_recursive(item, depth + 1)
                        if result:
                            return result
        except PermissionError:
            pass
        
        return None
    
    def _detect_language(self, entrypoint: str) -> Optional[str]:
        """Detect programming language from entrypoint file extension."""
        ext = Path(entrypoint).suffix.lower()
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".go": "go",
            ".php": "php",
            ".rb": "ruby",
            ".java": "java",
        }
        return language_map.get(ext)


def get_all_script_files(folder: str, max_depth: int = 3) -> list[str]:
    """
    Get all executable script files in a project folder.
    Returns relative paths from the project root.
    """
    folder_path = Path(folder)
    scripts = []
    
    def scan_folder(path: Path, depth: int, prefix: str = ""):
        if depth > max_depth:
            return
        
        try:
            for item in sorted(path.iterdir()):
                if item.is_file():
                    # Check if it's a known script type
                    if item.suffix.lower() in {".py", ".js", ".ts", ".go", ".php", ".rb"}:
                        rel_path = f"{prefix}{item.name}" if prefix else item.name
                        scripts.append(rel_path)
                elif item.is_dir() and item.name not in SKIP_FOLDERS:
                    new_prefix = f"{prefix}{item.name}/" if prefix else f"{item.name}/"
                    scan_folder(item, depth + 1, new_prefix)
        except PermissionError:
            pass
    
    scan_folder(folder_path, 0)
    return scripts
