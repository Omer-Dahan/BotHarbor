# BotHarbor - Codebase Context

## Overview
BotHarbor is a Windows desktop application designed to manage and run multiple Python Telegram bots simultaneously. It provides a GUI to add, edit, control (start/stop), and monitor the logs of these bot processes.

**Tech Stack:**
- **Language:** Python 3.10+
- **GUI:** CustomTkinter (Modern Tkinter wrapper)
- **Database:** SQLite with SQLAlchemy ORM
- **Process Management:** `subprocess` module with threading for non-blocking I/O

## Project Structure

### Root Directory
- `src/`: Source code directory.
- `pyproject.toml`: Configuration for build system and dependencies.
- `installer.iss`: Inno Setup script for creating the Windows installer.
- `build.bat`: Script to compile the application using PyInstaller.

### `src/botharbor` Package
The main application package is organized into several modules:

#### 1. Core (`src/botharbor/core/`)
Handles the business logic and backend functionality.
- **`process_manager.py`**: The heart of the application. It manages the lifecycle of bot processes (start, stop, crash detection). It uses `subprocess.Popen` to run bots and threads to capture `stdout` and `stderr` without freezing the UI. It emits events (callbacks) for status updates and logs.
- **`config.py`**: Application constants and version info.
- **`log_handler.py`**: Manages log storage and formatting for running processes.

#### 2. Database (`src/botharbor/database/`)
Handles data persistence using SQLite.
- **`models.py`**: Defines the SQLAlchemy `Project` model (id, name, path, entrypoint, interpreter).
- **`crud.py`**: Functions to Create, Read, Update, and Delete projects in the database.
- **`database.py`**: Database creation and connection management.

#### 3. UI (`src/botharbor/ui/`)
Contains all GUI components built with CustomTkinter.
- **`main_window.py`**: The entry point for the UI. It assembles the `Dashboard` and `LogPanel`, and binds `ProcessManager` callbacks to UI updates.
- **`dashboard.py`**: displays the list of projects, their status (Running/Stopped), and uptime. Handles user actions like Start/Stop/Edit.
- **`log_panel.py`**: Shows real-time logs for the selected project.
- **`dialogs.py`**: Popups for adding or editing projects.
- **`icons.py`**: Manages loading and caching of UI assets.

#### 4. Utils (`src/botharbor/utils/`)
- **`helpers.py`**: Helper functions (e.g., uptime formatting).

## Key Workflows

### Application Startup
1. **Entry Point**: `src/botharbor/main.py`.
2. **Initialization**:
   - Initializes the local SQLite database.
   - Sets CustomTkinter theme (Dark/Blue).
   - Instantiates `MainWindow`.
3. **Run**: Enters the main GUI event loop (`app.mainloop()`).

### Process Management Flow
1. **Starting a Bot**:
   - User clicks "Start" in `Dashboard`.
   - `Dashboard` calls `ProcessManager.start_project(project)`.
   - `ProcessManager`:
     - Checks if file and interpreter exist.
     - Spawns a subprocess using `subprocess.Popen`.
     - Starts background threads to read `stdout` and `stderr`.
     - Emits `on_status_changed` event (STARTING -> RUNNING).
2. **Monitoring**:
   - A dedicated monitor thread waits for the process to exit.
   - Separate threads read output streams line-by-line and emit `on_log_received`.
3. **Stopping a Bot**:
   - User clicks "Stop".
   - `ProcessManager` sends `SIGTERM` (terminate) to the subprocess.
   - If it doesn't close within timeout, it forces kill (`SIGKILL`).

### Logging System
- Logs are captured from standard output/error of the child processes.
- They are streamed in real-time to the `LogPanel` in the UI via callbacks.
- `ProcessManager` keeps a history of recent logs for crash analysis.

## Detailed Function Descriptions (Selected)

### `ProcessManager` (Core)
- `start_project(project)`: Prepares environment variables (UTF-8), launches the bot process, and attaches log readers.
- `stop_project(id)`: Safely terminates a bot process.
- `get_status(id)`: Returns current state (RUNNING, STOPPED, CRASHED).
- `_read_output(...)`: Background thread function that pushes log lines to the UI.

### `Dashboard` (UI)
- `_refresh_projects()`: Fetches project list from DB and rebuilds the UI list.
- `_update_uptimes()`: Runs every second to update the uptime counter for running bots.
- `_on_server_event(...)`: Receives signals from `ProcessManager` to update the GUI thread-safely.
