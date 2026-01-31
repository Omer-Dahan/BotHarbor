
"""Dashboard widget with project table using CustomTkinter."""

import customtkinter as ctk
from tkinter import messagebox
from typing import Callable, Optional

from hamal.database.crud import get_all_projects, get_project_by_id, delete_project
from hamal.database.models import Project
from hamal.core.process_manager import ProcessManager, ProcessStatus
from hamal.utils.helpers import format_uptime
from hamal.ui.icons import Icons



# Catppuccin Mocha colors
COLORS = {
    "base": "#1e1e2e",
    "surface": "#313244",
    "overlay": "#45475a",
    "text": "#cdd6f4",
    "subtext": "#a6adc8",
    "green": "#a6e3a1",
    "red": "#f38ba8",
    "blue": "#89b4fa",
    "yellow": "#f9e2af",
    "mauve": "#cba6f7",
}


class Dashboard(ctk.CTkFrame):
    """Main dashboard with project table and controls."""
    
    def __init__(
        self, 
        master, 
        process_manager: ProcessManager,
        on_view_logs: Callable[[int, str], None],
        **kwargs
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.process_manager = process_manager
        self.on_view_logs = on_view_logs
        self.project_rows: dict[int, dict] = {}  # project_id -> row widgets
        
        # Ensure icons are loaded
        Icons.load()
        
        self._setup_ui()
        self._refresh_projects()
        
        # Start uptime update timer
        self._update_uptimes()
    
    def _setup_ui(self):
        """Setup the dashboard UI."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # === HEADER ===
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.grid(row=0, column=0, padx=5, pady=(5, 10), sticky="ew")
        self.header.grid_columnconfigure(0, weight=1)
        
        # Title
        self.title = ctk.CTkLabel(
            self.header,
            text="Projects",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=COLORS["text"]
        )
        self.title.grid(row=0, column=0, sticky="w", padx=5)
        
        # Buttons frame
        self.buttons_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        self.buttons_frame.grid(row=0, column=1, sticky="e")
        
        # Start All button
        self.start_all_btn = ctk.CTkButton(
            self.buttons_frame,
            text="Start All",
            image=Icons.get("play"),
            font=ctk.CTkFont(size=12, weight="bold"),
            width=110,
            height=32,
            corner_radius=6,
            fg_color=COLORS["green"],
            hover_color="#86c381",
            text_color="#1e1e2e",
            compound="left",
            command=self._on_start_all
        )
        self.start_all_btn.pack(side="left", padx=3)
        
        # Stop All button
        self.stop_all_btn = ctk.CTkButton(
            self.buttons_frame,
            text="Stop All",
            image=Icons.get("stop"),
            font=ctk.CTkFont(size=12, weight="bold"),
            width=110,
            height=32,
            corner_radius=6,
            fg_color=COLORS["red"],
            hover_color="#e06080",
            text_color="#1e1e2e",
            compound="left",
            command=self._on_stop_all
        )
        self.stop_all_btn.pack(side="left", padx=3)
        
        # Add Project button
        self.add_btn = ctk.CTkButton(
            self.buttons_frame,
            text="Add Project",
            image=Icons.get("plus"),
            font=ctk.CTkFont(size=12, weight="bold"),
            width=130,
            height=32,
            corner_radius=6,
            fg_color=COLORS["blue"],
            hover_color="#6994d8",
            text_color="#1e1e2e",
            compound="left",
            command=self._on_add_project
        )
        self.add_btn.pack(side="left", padx=3)
        
        # === TABLE CONTAINER ===
        self.table_container = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=8)
        self.table_container.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.table_container.grid_columnconfigure(0, weight=1)
        self.table_container.grid_rowconfigure(1, weight=1)
        
        # Table header
        self.table_header = ctk.CTkFrame(self.table_container, fg_color=COLORS["overlay"], corner_radius=0)
        self.table_header.grid(row=0, column=0, sticky="ew", padx=2, pady=(2, 0))
        
        # Header columns
        headers = [("Project", 180), ("Status", 100), ("Uptime", 90), ("Actions", 200)]
        for i, (text, width) in enumerate(headers):
            lbl = ctk.CTkLabel(
                self.table_header,
                text=text,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS["subtext"],
                width=width,
                anchor="w" if i == 0 else "center"
            )
            lbl.grid(row=0, column=i, padx=10, pady=8, sticky="w" if i == 0 else "")
        
        self.table_header.grid_columnconfigure(0, weight=1)
        
        # Scrollable table body
        self.table_body = ctk.CTkScrollableFrame(
            self.table_container,
            fg_color="transparent",
            scrollbar_button_color=COLORS["overlay"],
            scrollbar_button_hover_color=COLORS["blue"]
        )
        self.table_body.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)
        self.table_body.grid_columnconfigure(0, weight=1)
        
        # Empty state
        self.empty_label = ctk.CTkLabel(
            self.table_body,
            text="No projects yet.\nClick '+ Add Project' to get started!",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["subtext"]
        )
    
    def _refresh_projects(self):
        """Refresh the project list from database."""
        # Clear existing rows
        for row_widgets in self.project_rows.values():
            row_widgets["frame"].destroy()
        self.project_rows.clear()
        
        # Get projects
        projects = get_all_projects()
        
        if not projects:
            self.empty_label.grid(row=0, column=0, pady=50)
            return
        
        self.empty_label.grid_forget()
        
        # Create rows
        for i, project in enumerate(projects):
            self._create_project_row(i, project)
    
    def _create_project_row(self, row_index: int, project: Project):
        """Create a single project row."""
        status = self.process_manager.get_status(project.id)
        
        # Row frame
        row_frame = ctk.CTkFrame(self.table_body, fg_color="transparent", height=50)
        row_frame.grid(row=row_index, column=0, sticky="ew", pady=1)
        row_frame.grid_columnconfigure(0, weight=1)
        
        # Project name
        name_label = ctk.CTkLabel(
            row_frame,
            text=project.name,
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text"],
            width=180,
            anchor="w"
        )
        name_label.grid(row=0, column=0, padx=10, pady=8, sticky="w")
        
        # Status with dot
        status_frame = ctk.CTkFrame(row_frame, fg_color="transparent", width=100)
        status_frame.grid(row=0, column=1, padx=10, pady=8)
        
        status_dot = ctk.CTkLabel(
            status_frame,
            text="●",
            font=ctk.CTkFont(size=10),
            width=15
        )
        status_dot.pack(side="left")
        
        status_text = ctk.CTkLabel(
            status_frame,
            text="Stopped",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["subtext"]
        )
        status_text.pack(side="left", padx=2)
        
        # Uptime
        uptime_label = ctk.CTkLabel(
            row_frame,
            text="-",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["subtext"],
            width=90
        )
        uptime_label.grid(row=0, column=2, padx=10, pady=8)
        
        # Actions frame
        actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent", width=200)
        actions_frame.grid(row=0, column=3, padx=10, pady=8)
        
        # Play button
        play_btn = ctk.CTkButton(
            actions_frame,
            text="",
            image=Icons.get("play"),
            width=32,
            height=32,
            corner_radius=4,
            fg_color=COLORS["green"],
            hover_color="#86c381",
            text_color="#1e1e2e",
            command=lambda pid=project.id: self._on_start_project(pid)
        )
        play_btn.pack(side="left", padx=2)
        
        # Stop button
        stop_btn = ctk.CTkButton(
            actions_frame,
            text="",
            image=Icons.get("stop"),
            width=32,
            height=32,
            corner_radius=4,
            fg_color=COLORS["red"],
            hover_color="#e06080",
            text_color="#1e1e2e",
            command=lambda pid=project.id: self._on_stop_project(pid)
        )
        stop_btn.pack(side="left", padx=2)
        
        # Log button
        log_btn = ctk.CTkButton(
            actions_frame,
            text="",
            image=Icons.get("logs"),
            width=32,
            height=32,
            corner_radius=4,
            fg_color=COLORS["overlay"],
            hover_color=COLORS["blue"],
            text_color=COLORS["text"],
            command=lambda pid=project.id, pname=project.name: self.on_view_logs(pid, pname)
        )
        log_btn.pack(side="left", padx=2)
        
        # Settings/Edit button
        edit_btn = ctk.CTkButton(
            actions_frame,
            text="",
            image=Icons.get("settings"),
            width=32,
            height=32,
            corner_radius=4,
            fg_color=COLORS["overlay"],
            hover_color=COLORS["mauve"],
            text_color=COLORS["text"],
            command=lambda pid=project.id: self._on_edit_project(pid)
        )
        edit_btn.pack(side="left", padx=2)
        
        # Delete button
        delete_btn = ctk.CTkButton(
            actions_frame,
            text="",
            image=Icons.get("trash"),
            width=32,
            height=32,
            corner_radius=4,
            fg_color=COLORS["overlay"],
            hover_color=COLORS["red"],
            text_color=COLORS["subtext"],
            command=lambda pid=project.id, pname=project.name: self._on_delete_project(pid, pname)
        )
        delete_btn.pack(side="left", padx=2)
        
        # Store widgets for updates
        self.project_rows[project.id] = {
            "frame": row_frame,
            "name": name_label,
            "status_dot": status_dot,
            "status_text": status_text,
            "uptime": uptime_label,
            "play_btn": play_btn,
            "stop_btn": stop_btn,
            "project": project
        }
        
        # Update initial status
        self._update_row_status(project.id, status)
    
    def _update_row_status(self, project_id: int, status: ProcessStatus):
        """Update the visual status of a project row."""
        if project_id not in self.project_rows:
            return
        
        row = self.project_rows[project_id]
        
        # Colors and text for each status
        status_config = {
            ProcessStatus.STOPPED: (COLORS["subtext"], "Stopped", False),
            ProcessStatus.STARTING: (COLORS["yellow"], "Starting...", False),
            ProcessStatus.RUNNING: (COLORS["green"], "Running", True),
            ProcessStatus.STOPPING: (COLORS["yellow"], "Stopping...", False),
            ProcessStatus.CRASHED: (COLORS["red"], "Crashed", False),
        }
        
        color, text, is_running = status_config.get(status, (COLORS["subtext"], "Unknown", False))
        
        row["status_dot"].configure(text_color=color)
        row["status_text"].configure(text=text, text_color=color)
        
        if not is_running:
            row["uptime"].configure(text="-")
    
    def _on_add_project(self):
        """Show add project dialog."""
        from hamal.ui.dialogs import AddProjectDialog
        dialog = AddProjectDialog(self.winfo_toplevel())
        if dialog.get_result():
            self._refresh_projects()
        
    def _on_start_project(self, project_id: int):
        """Start a project."""
        project = get_project_by_id(project_id)
        if project:
            self.process_manager.start_project(project)
    
    def _on_stop_project(self, project_id: int):
        """Stop a project."""
        self.process_manager.stop_project(project_id)
    
    def _on_edit_project(self, project_id: int):
        """Edit a project."""
        from hamal.ui.dialogs import EditProjectDialog
        project = get_project_by_id(project_id)
        if project:
            dialog = EditProjectDialog(self.winfo_toplevel(), project)
            if dialog.get_result():
                self._refresh_projects()
    
    def _on_delete_project(self, project_id: int, project_name: str):
        """Delete a project."""
        if not messagebox.askyesno(
            "Confirm Delete",
            f"Delete project '{project_name}'?\nThis cannot be undone."
        ):
            return
        
        self.process_manager.stop_project(project_id)
        delete_project(project_id)
        self._refresh_projects()
    
    def _on_start_all(self):
        """Start all stopped projects."""
        projects = get_all_projects()
        for project in projects:
            status = self.process_manager.get_status(project.id)
            if status in (ProcessStatus.STOPPED, ProcessStatus.CRASHED):
                self.process_manager.start_project(project)
    
    def _on_stop_all(self):
        """Stop all running projects."""
        self.process_manager.stop_all()
    
    def update_project_status(self, project_id: int, status_str: str):
        """Update a project's status display."""
        try:
            status = ProcessStatus(status_str)
            self._update_row_status(project_id, status)
        except ValueError:
            pass
    
    def _update_uptimes(self):
        """Update uptime display for running projects."""
        for project_id, row in self.project_rows.items():
            status = self.process_manager.get_status(project_id)
            if status == ProcessStatus.RUNNING:
                uptime = self.process_manager.get_uptime(project_id)
                if uptime is not None:
                    row["uptime"].configure(text=format_uptime(uptime))
        
        self.after(1000, self._update_uptimes)
    
    def get_project_count(self) -> int:
        """Get total number of projects."""
        return len(self.project_rows)
    
    def get_running_count(self) -> int:
        """Get number of running projects."""
        count = 0
        for project_id in self.project_rows:
            if self.process_manager.get_status(project_id) == ProcessStatus.RUNNING:
                count += 1
        return count
