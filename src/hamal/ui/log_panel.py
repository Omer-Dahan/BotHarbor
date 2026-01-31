"""Log panel widget using CustomTkinter - Live logs view."""

import os
import customtkinter as ctk
from pathlib import Path
from typing import Optional

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
}


class LogPanel(ctk.CTkFrame):
    """Panel for displaying LIVE project logs."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.current_project_id: Optional[int] = None
        self.current_project_name: str = ""
        self.logs: dict[int, list[str]] = {}
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the log panel UI."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # === HEADER ===
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.grid(row=0, column=0, padx=5, pady=(5, 5), sticky="ew")
        self.header.grid_columnconfigure(0, weight=1)
        
        # Title with project name
        self.title = ctk.CTkLabel(
            self.header,
            text="Logs",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text"]
        )
        self.title.grid(row=0, column=0, sticky="w", padx=5)
        
        # Buttons frame
        self.buttons_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        self.buttons_frame.grid(row=0, column=1, sticky="e")
        
        # Live indicator
        self.live_label = ctk.CTkLabel(
            self.buttons_frame,
            text="● LIVE",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["green"]
        )
        self.live_label.pack(side="left", padx=10)
        
        # Open Folder button
        self.open_folder_btn = ctk.CTkButton(
            self.buttons_frame,
            text="Open Folder",
            font=ctk.CTkFont(size=11),
            width=85,
            height=28,
            corner_radius=4,
            fg_color=COLORS["blue"],
            hover_color="#6994d8",
            text_color="#1e1e2e",
            command=self._on_open_folder
        )
        self.open_folder_btn.pack(side="left", padx=3)
        
        # Clear button
        self.clear_btn = ctk.CTkButton(
            self.buttons_frame,
            text="Clear",
            font=ctk.CTkFont(size=11),
            width=55,
            height=28,
            corner_radius=4,
            fg_color=COLORS["overlay"],
            hover_color=COLORS["red"],
            text_color=COLORS["text"],
            command=self._clear_logs
        )
        self.clear_btn.pack(side="left", padx=3)
        
        # === LOG TEXT AREA ===
        self.log_container = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=8)
        self.log_container.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.log_container.grid_columnconfigure(0, weight=1)
        self.log_container.grid_rowconfigure(0, weight=1)
        
        self.log_text = ctk.CTkTextbox(
            self.log_container,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color=COLORS["base"],
            text_color=COLORS["text"],
            scrollbar_button_color=COLORS["overlay"],
            scrollbar_button_hover_color=COLORS["blue"],
            wrap="none",
            corner_radius=6
        )
        self.log_text.grid(row=0, column=0, padx=3, pady=3, sticky="nsew")
        self.log_text.configure(state="disabled")
        
        # Initial message
        self._show_initial_message()
        
        # === STATUS BAR ===
        self.status_bar = ctk.CTkLabel(
            self,
            text="Select a project to view live logs",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["subtext"],
            anchor="w"
        )
        self.status_bar.grid(row=2, column=0, padx=10, pady=(0, 5), sticky="ew")
    
    def _show_initial_message(self):
        """Show initial message when no project is selected."""
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.insert("end", "\n\n    Select a project and click LOG to view live output.\n")
        self.log_text.configure(state="disabled")
    
    def set_project(self, project_id: int, project_name: str):
        """Set the current project to display live logs for."""
        self.current_project_id = project_id
        self.current_project_name = project_name
        
        # Update title
        self.title.configure(text=f"Logs - {project_name}")
        
        # Show live indicator
        self.live_label.configure(text="● LIVE", text_color=COLORS["green"])
        
        # Update status
        self.status_bar.configure(text=f"Viewing live logs for: {project_name}")
        
        # Display existing live logs for this project
        self._display_logs()
    
    def _on_open_folder(self):
        """Open the logs folder in file explorer."""
        if not self.current_project_id:
            return
        
        logs_dir = get_project_logs_dir(self.current_project_id)
        if logs_dir.exists():
            os.startfile(str(logs_dir))
    
    def add_log(self, project_id: int, line: str):
        """Add a live log line for a project."""
        if project_id not in self.logs:
            self.logs[project_id] = []
        
        self.logs[project_id].append(line)
        
        # Keep only last 1000 lines
        if len(self.logs[project_id]) > 1000:
            self.logs[project_id] = self.logs[project_id][-1000:]
        
        # If this is the current project, display the new line
        if project_id == self.current_project_id:
            self._append_line(line)
    
    def _display_logs(self):
        """Display all live logs for the current project."""
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        
        if self.current_project_id and self.current_project_id in self.logs:
            for line in self.logs[self.current_project_id]:
                self.log_text.insert("end", line + "\n")
        else:
            self.log_text.insert("end", f"\n    Waiting for output from {self.current_project_name}...\n")
            self.log_text.insert("end", "    Start the project to see live logs.\n")
        
        self.log_text.configure(state="disabled")
        self.log_text.see("end")
    
    def _append_line(self, line: str):
        """Append a single line to the log display."""
        self.log_text.configure(state="normal")
        self.log_text.insert("end", line + "\n")
        self.log_text.configure(state="disabled")
        self.log_text.see("end")
    
    def _clear_logs(self):
        """Clear logs for the current project."""
        if self.current_project_id:
            self.logs[self.current_project_id] = []
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")
