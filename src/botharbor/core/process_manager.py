"""Process management for bot projects."""

import subprocess
import threading
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, Signal, QMetaObject, Qt, Q_ARG

from botharbor.core.log_handler import LogHandler
from botharbor.database.models import Project


class ProcessStatus(Enum):
    """Runtime status of a project process."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    CRASHED = "crashed"


@dataclass
class ProcessInfo:
    """Runtime information about a running process."""
    process: subprocess.Popen
    start_time: datetime
    log_handler: LogHandler
    reader_thread: Optional[threading.Thread] = None
    recent_logs: list = None  # Store last N log lines
    
    # Error detection patterns
    ERROR_PATTERNS = ["Traceback", "Error:", "Exception:", "error:", "CRITICAL", "FATAL"]
    
    def __post_init__(self):
        if self.recent_logs is None:
            self.recent_logs = []
    
    def add_log(self, line: str):
        """Add a log line, keeping only last 150 lines."""
        self.recent_logs.append(line)
        if len(self.recent_logs) > 150:
            self.recent_logs.pop(0)
    
    def get_recent_logs(self) -> str:
        """Get recent logs as a string."""
        return "\n".join(self.recent_logs)
    
    def get_error_logs(self) -> str:
        """Get logs starting from the first error indicator."""
        # Find first line with error pattern
        error_start_idx = None
        for i, line in enumerate(self.recent_logs):
            for pattern in self.ERROR_PATTERNS:
                if pattern in line:
                    error_start_idx = i
                    break
            if error_start_idx is not None:
                break
        
        if error_start_idx is not None:
            # Return from error start to end
            error_logs = self.recent_logs[error_start_idx:]
            return "\n".join(error_logs)
        else:
            # No error pattern found, return last 30 lines
            return "\n".join(self.recent_logs[-30:])


class ProcessManager(QObject):
    """
    Manages subprocess lifecycle for bot projects.
    
    Tracks runtime status in-memory (not persisted to database).
    Emits Qt signals for UI updates.
    """

    # Signals
    status_changed = Signal(int, str)  # project_id, status (as string)
    log_received = Signal(int, str)    # project_id, log_line
    process_exited = Signal(int, int)  # project_id, exit_code
    crash_detected = Signal(int, str, int, str)  # project_id, project_name, exit_code, recent_logs

    def __init__(self, parent=None):
        super().__init__(parent)
        self._processes: dict[int, ProcessInfo] = {}
        self._project_names: dict[int, str] = {}  # Store project names for crash notifications
        self._lock = threading.Lock()

    def get_status(self, project_id: int) -> ProcessStatus:
        """Get the current status of a project."""
        with self._lock:
            if project_id not in self._processes:
                return ProcessStatus.STOPPED
            
            info = self._processes[project_id]
            # Check if process is still alive
            if info.process.poll() is not None:
                # Process has exited
                return ProcessStatus.CRASHED if info.process.returncode != 0 else ProcessStatus.STOPPED
            
            return ProcessStatus.RUNNING

    def get_uptime(self, project_id: int) -> Optional[float]:
        """Get the uptime in seconds for a running project. Returns None if not running."""
        with self._lock:
            if project_id not in self._processes:
                return None
            
            info = self._processes[project_id]
            if info.process.poll() is not None:
                return None
            
            return (datetime.now() - info.start_time).total_seconds()

    def start_project(self, project: Project) -> bool:
        """
        Start a project subprocess.
        Returns True if started successfully, False otherwise.
        """
        with self._lock:
            # Check if already running
            if project.id in self._processes:
                existing = self._processes[project.id]
                if existing.process.poll() is None:
                    return False  # Already running

        # Emit starting status (outside lock)
        self._emit_status(project.id, ProcessStatus.STARTING.value)

        try:
            # Prepare the command
            interpreter = Path(project.interpreter_path)
            script = Path(project.folder_path) / project.entrypoint
            
            if not interpreter.exists():
                self._emit_status(project.id, ProcessStatus.STOPPED.value)
                return False
            
            if not script.exists():
                self._emit_status(project.id, ProcessStatus.STOPPED.value)
                return False

            # Create log handler
            log_handler = LogHandler(project.id)
            log_handler.start_logging()

            # Set up environment with UTF-8 encoding
            import os
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            env["PYTHONUTF8"] = "1"

            # Start the subprocess with UTF-8 encoding
            process = subprocess.Popen(
                [str(interpreter), "-u", str(script)],  # -u for unbuffered output
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=project.folder_path,
                text=True,
                encoding="utf-8",
                errors="replace",  # Replace chars that can't be decoded
                bufsize=1,  # Line buffered
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW  # No console window on Windows
            )

            # Create process info
            info = ProcessInfo(
                process=process,
                start_time=datetime.now(),
                log_handler=log_handler
            )

            # Start reader threads
            stdout_thread = threading.Thread(
                target=self._read_output,
                args=(project.id, process.stdout, "stdout"),
                daemon=True
            )
            stderr_thread = threading.Thread(
                target=self._read_output,
                args=(project.id, process.stderr, "stderr"),
                daemon=True
            )
            stdout_thread.start()
            stderr_thread.start()

            # Start monitor thread
            monitor_thread = threading.Thread(
                target=self._monitor_process,
                args=(project.id,),
                daemon=True
            )
            monitor_thread.start()

            with self._lock:
                self._processes[project.id] = info
                self._project_names[project.id] = project.name

            self._emit_status(project.id, ProcessStatus.RUNNING.value)
            return True

        except Exception as e:
            self._emit_log(project.id, f"[ERROR] Failed to start: {e}")
            self._emit_status(project.id, ProcessStatus.STOPPED.value)
            return False

    def _emit_status(self, project_id: int, status: str):
        """Thread-safe status signal emission."""
        self.status_changed.emit(project_id, status)

    def _emit_log(self, project_id: int, line: str):
        """Thread-safe log signal emission."""
        self.log_received.emit(project_id, line)

    def stop_project(self, project_id: int) -> bool:
        """
        Stop a running project.
        Returns True if stopped successfully, False if not running.
        """
        with self._lock:
            if project_id not in self._processes:
                return False
            
            info = self._processes[project_id]
            if info.process.poll() is not None:
                # Already stopped
                return False

        self._emit_status(project_id, ProcessStatus.STOPPING.value)

        try:
            info.process.terminate()
            
            # Wait up to 5 seconds for graceful shutdown
            try:
                info.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill
                info.process.kill()
                info.process.wait()

            # Stop logging
            info.log_handler.stop_logging()

            with self._lock:
                del self._processes[project_id]

            self._emit_status(project_id, ProcessStatus.STOPPED.value)
            return True

        except Exception as e:
            self._emit_log(project_id, f"[ERROR] Failed to stop: {e}")
            return False

    def stop_all(self):
        """Stop all running projects."""
        with self._lock:
            project_ids = list(self._processes.keys())
        
        for project_id in project_ids:
            self.stop_project(project_id)

    def _read_output(self, project_id: int, stream, stream_name: str):
        """Read output from a subprocess stream and emit signals."""
        try:
            for line in iter(stream.readline, ""):
                if not line:
                    break
                line = line.rstrip("\n\r")
                
                # Write to log file and store for crash notifications
                with self._lock:
                    if project_id in self._processes:
                        info = self._processes[project_id]
                        info.log_handler.write_line(line, stream_name)
                        info.add_log(f"[{stream_name.upper()}] {line}")
                
                # Emit signal for UI (thread-safe)
                self._emit_log(project_id, line)
        except Exception:
            pass
        finally:
            stream.close()

    def _monitor_process(self, project_id: int):
        """Monitor a process and emit exit signal when it terminates."""
        with self._lock:
            if project_id not in self._processes:
                return
            process = self._processes[project_id].process

        # Wait for process to complete
        exit_code = process.wait()

        # Get info for crash notification before cleanup
        recent_logs = ""
        project_name = ""
        with self._lock:
            if project_id in self._processes:
                info = self._processes[project_id]
                recent_logs = info.get_error_logs()
                info.log_handler.stop_logging()
                del self._processes[project_id]
            project_name = self._project_names.get(project_id, f"Project {project_id}")

        # Emit signals (thread-safe)
        status = ProcessStatus.CRASHED if exit_code != 0 else ProcessStatus.STOPPED
        self._emit_status(project_id, status.value)
        self.process_exited.emit(project_id, exit_code)
        
        # Emit crash notification if process crashed
        if exit_code != 0:
            self.crash_detected.emit(project_id, project_name, exit_code, recent_logs)

    def get_log_handler(self, project_id: int) -> Optional[LogHandler]:
        """Get the log handler for a project (if running)."""
        with self._lock:
            if project_id in self._processes:
                return self._processes[project_id].log_handler
        return None
