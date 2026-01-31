"""Process management for projects - Callback-based (no Qt dependency)."""

import subprocess
import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Callable

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
    recent_logs: list = field(default_factory=list)
    
    # Error detection patterns
    ERROR_PATTERNS = ["Traceback", "Error:", "Exception:", "error:", "CRITICAL", "FATAL"]
    
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
        error_start_idx = None
        for i, line in enumerate(self.recent_logs):
            for pattern in self.ERROR_PATTERNS:
                if pattern in line:
                    error_start_idx = i
                    break
            if error_start_idx is not None:
                break
        
        if error_start_idx is not None:
            return "\n".join(self.recent_logs[error_start_idx:])
        else:
            return "\n".join(self.recent_logs[-30:])


class ProcessManager:
    """
    Manages subprocess lifecycle for projects.
    
    Uses callback functions instead of Qt signals for UI updates.
    """

    def __init__(self):
        self._processes: dict[int, ProcessInfo] = {}
        self._project_names: dict[int, str] = {}
        self._lock = threading.Lock()
        
        # Callbacks (set by UI)
        self.on_status_changed: Optional[Callable[[int, str], None]] = None
        self.on_log_received: Optional[Callable[[int, str], None]] = None
        self.on_process_exited: Optional[Callable[[int, int], None]] = None
        self.on_crash_detected: Optional[Callable[[int, str, int, str], None]] = None

    def get_status(self, project_id: int) -> ProcessStatus:
        """Get the current status of a project."""
        with self._lock:
            if project_id not in self._processes:
                return ProcessStatus.STOPPED
            
            info = self._processes[project_id]
            if info.process.poll() is not None:
                return ProcessStatus.CRASHED if info.process.returncode != 0 else ProcessStatus.STOPPED
            
            return ProcessStatus.RUNNING

    def get_uptime(self, project_id: int) -> Optional[float]:
        """Get the uptime in seconds for a running project."""
        with self._lock:
            if project_id not in self._processes:
                return None
            
            info = self._processes[project_id]
            if info.process.poll() is not None:
                return None
            
            return (datetime.now() - info.start_time).total_seconds()

    def start_project(self, project: Project) -> bool:
        """Start a project subprocess."""
        with self._lock:
            if project.id in self._processes:
                existing = self._processes[project.id]
                if existing.process.poll() is None:
                    return False

        self._emit_status(project.id, ProcessStatus.STARTING.value)

        try:
            interpreter = Path(project.interpreter_path)
            script = Path(project.folder_path) / project.entrypoint
            
            if not interpreter.exists():
                self._emit_status(project.id, ProcessStatus.STOPPED.value)
                return False
            
            if not script.exists():
                self._emit_status(project.id, ProcessStatus.STOPPED.value)
                return False

            log_handler = LogHandler(project.id)
            log_handler.start_logging()

            import os
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            env["PYTHONUTF8"] = "1"

            process = subprocess.Popen(
                [str(interpreter), "-u", str(script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=project.folder_path,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            info = ProcessInfo(
                process=process,
                start_time=datetime.now(),
                log_handler=log_handler
            )

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
        """Emit status change via callback."""
        if self.on_status_changed:
            self.on_status_changed(project_id, status)

    def _emit_log(self, project_id: int, line: str):
        """Emit log line via callback."""
        if self.on_log_received:
            self.on_log_received(project_id, line)

    def stop_project(self, project_id: int) -> bool:
        """Stop a running project."""
        with self._lock:
            if project_id not in self._processes:
                return False
            
            info = self._processes[project_id]
            if info.process.poll() is not None:
                return False

        self._emit_status(project_id, ProcessStatus.STOPPING.value)

        try:
            info.process.terminate()
            
            try:
                info.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                info.process.kill()
                info.process.wait()

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
        """Read output from a subprocess stream."""
        try:
            for line in iter(stream.readline, ""):
                if not line:
                    break
                line = line.rstrip("\n\r")
                
                with self._lock:
                    if project_id in self._processes:
                        info = self._processes[project_id]
                        info.log_handler.write_line(line, stream_name)
                        info.add_log(f"[{stream_name.upper()}] {line}")
                
                self._emit_log(project_id, line)
        except Exception:
            pass
        finally:
            stream.close()

    def _monitor_process(self, project_id: int):
        """Monitor a process and handle exit."""
        with self._lock:
            if project_id not in self._processes:
                return
            process = self._processes[project_id].process

        exit_code = process.wait()

        recent_logs = ""
        project_name = ""
        with self._lock:
            if project_id in self._processes:
                info = self._processes[project_id]
                recent_logs = info.get_error_logs()
                info.log_handler.stop_logging()
                del self._processes[project_id]
            project_name = self._project_names.get(project_id, f"Project {project_id}")

        status = ProcessStatus.CRASHED if exit_code != 0 else ProcessStatus.STOPPED
        self._emit_status(project_id, status.value)
        
        if self.on_process_exited:
            self.on_process_exited(project_id, exit_code)
        
        if exit_code != 0 and self.on_crash_detected:
            self.on_crash_detected(project_id, project_name, exit_code, recent_logs)

    def get_log_handler(self, project_id: int) -> Optional[LogHandler]:
        """Get the log handler for a project (if running)."""
        with self._lock:
            if project_id in self._processes:
                return self._processes[project_id].log_handler
        return None
