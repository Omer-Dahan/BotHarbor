"""Main application window using CustomTkinter."""

import customtkinter as ctk
from tkinter import messagebox

from botharbor.core.config import APP_NAME, APP_VERSION
from botharbor.core.process_manager import ProcessManager
from botharbor.ui.dashboard import Dashboard
from botharbor.ui.log_panel import LogPanel


# Catppuccin Mocha colors
COLORS = {
    "base": "#1e1e2e",
    "mantle": "#181825",
    "crust": "#11111b",
    "surface": "#313244",
    "overlay": "#45475a",
    "text": "#cdd6f4",
    "subtext": "#a6adc8",
    "blue": "#89b4fa",
    "red": "#f38ba8",
    "green": "#a6e3a1",
    "yellow": "#f9e2af",
    "mauve": "#cba6f7",
}


class MainWindow(ctk.CTk):
    """Main application window with dashboard and log viewer."""
    
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title(f"{APP_NAME}")
        self.geometry("1100x650")
        self.minsize(900, 500)
        
        # Set dark appearance
        self.configure(fg_color=COLORS["base"])
        
        # Process manager
        self.process_manager = ProcessManager()
        
        # Setup callbacks
        self._setup_callbacks()
        
        # Build UI
        self._setup_menu()
        self._setup_ui()
        
        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _setup_callbacks(self):
        """Setup process manager callbacks."""
        self.process_manager.on_status_changed = self._on_status_changed
        self.process_manager.on_log_received = self._on_log_received
        self.process_manager.on_crash_detected = self._on_crash_detected
    
    def _setup_menu(self):
        """Setup a custom dark-themed menu bar using CTkFrame."""
        # Custom menu bar frame
        self.custom_menu_bar = ctk.CTkFrame(
            self, 
            fg_color=COLORS["crust"], 
            height=28,
            corner_radius=0
        )
        self.custom_menu_bar.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.custom_menu_bar.grid_propagate(False)
        
        # Active dropdown tracking
        self._active_menu = None
        
        # Menu button style
        menu_btn_style = {
            "fg_color": "transparent",
            "hover_color": COLORS["surface"],
            "text_color": COLORS["text"],
            "font": ctk.CTkFont(size=12),
            "corner_radius": 0,
            "height": 28,
            "anchor": "center"
        }
        
        # File menu button
        self.file_btn = ctk.CTkButton(
            self.custom_menu_bar,
            text="File",
            width=50,
            command=lambda: self._toggle_dropdown("file"),
            **menu_btn_style
        )
        self.file_btn.pack(side="left", padx=0)
        
        # Projects menu button
        self.projects_btn = ctk.CTkButton(
            self.custom_menu_bar,
            text="Projects",
            width=70,
            command=lambda: self._toggle_dropdown("projects"),
            **menu_btn_style
        )
        self.projects_btn.pack(side="left", padx=0)
        
        # Help menu button
        self.help_btn = ctk.CTkButton(
            self.custom_menu_bar,
            text="Help",
            width=50,
            command=lambda: self._toggle_dropdown("help"),
            **menu_btn_style
        )
        self.help_btn.pack(side="left", padx=0)
        
        # Create dropdown menus (hidden by default)
        self._create_dropdowns()
    
    def _create_dropdowns(self):
        """Create dropdown menu frames."""
        dropdown_style = {
            "fg_color": COLORS["surface"],
            "corner_radius": 4,
            "border_width": 1,
            "border_color": COLORS["overlay"],
        }
        
        # Subtle hover - darker instead of bright purple
        item_style = {
            "fg_color": "transparent",
            "hover_color": COLORS["overlay"],
            "text_color": COLORS["text"],
            "font": ctk.CTkFont(size=12),
            "corner_radius": 4,
            "height": 26,
            "anchor": "w"
        }
        
        # File dropdown
        self.file_dropdown = ctk.CTkFrame(self, **dropdown_style)
        ctk.CTkButton(
            self.file_dropdown,
            text="Exit",
            width=100,
            command=lambda: self._menu_action(self._on_closing),
            **item_style
        ).pack(fill="x", padx=4, pady=4)
        
        # Projects dropdown
        self.projects_dropdown = ctk.CTkFrame(self, **dropdown_style)
        ctk.CTkButton(
            self.projects_dropdown,
            text="Add Project...",
            width=130,
            command=lambda: self._menu_action(self._on_add_project),
            **item_style
        ).pack(fill="x", padx=4, pady=(4, 2))
        
        # Separator
        sep = ctk.CTkFrame(self.projects_dropdown, fg_color=COLORS["overlay"], height=1)
        sep.pack(fill="x", padx=8, pady=2)
        
        ctk.CTkButton(
            self.projects_dropdown,
            text="Start All",
            width=130,
            command=lambda: self._menu_action(self._on_start_all),
            **item_style
        ).pack(fill="x", padx=4, pady=2)
        
        ctk.CTkButton(
            self.projects_dropdown,
            text="Stop All",
            width=130,
            command=lambda: self._menu_action(self._on_stop_all),
            **item_style
        ).pack(fill="x", padx=4, pady=(2, 4))
        
        # Help dropdown
        self.help_dropdown = ctk.CTkFrame(self, **dropdown_style)
        ctk.CTkButton(
            self.help_dropdown,
            text="About BotHarbor",
            width=130,
            command=lambda: self._menu_action(self._show_about),
            **item_style
        ).pack(fill="x", padx=4, pady=4)
        
        # Store dropdown references
        self._dropdowns = {
            "file": (self.file_dropdown, self.file_btn),
            "projects": (self.projects_dropdown, self.projects_btn),
            "help": (self.help_dropdown, self.help_btn)
        }
    
    def _toggle_dropdown(self, menu_name: str):
        """Toggle a dropdown menu visibility."""
        # If clicking the same menu, close it
        if self._active_menu == menu_name:
            self._hide_all_dropdowns()
            return
        
        # Hide any open dropdown
        self._hide_all_dropdowns()
        
        # Show the clicked dropdown
        dropdown, btn = self._dropdowns[menu_name]
        
        # Calculate position relative to the window
        btn.update_idletasks()
        x = btn.winfo_x()
        y = self.custom_menu_bar.winfo_height()
        
        dropdown.place(x=x, y=y)
        dropdown.lift()
        self._active_menu = menu_name
    
    def _hide_all_dropdowns(self):
        """Hide all dropdown menus."""
        for dropdown, _ in self._dropdowns.values():
            dropdown.place_forget()
        self._active_menu = None
    
    def _menu_action(self, action_func):
        """Execute a menu action and close dropdown."""
        self._hide_all_dropdowns()
        action_func()
    
    def _on_add_project(self):
        """Open add project dialog from menu."""
        self.dashboard._on_add_project()
    
    def _on_start_all(self):
        """Start all projects from menu."""
        self.dashboard._on_start_all()
    
    def _on_stop_all(self):
        """Stop all projects from menu."""
        self.dashboard._on_stop_all()
    
    def _show_about(self):
        """Show about dialog."""
        messagebox.showinfo(
            "About BotHarbor",
            f"BotHarbor v{APP_VERSION}\n\n"
            f"A modern script runner for managing\nyour bots and projects.\n\n"
            f"Built with CustomTkinter"
        )
    
    def _setup_ui(self):
        """Setup the main UI layout."""
        # Configure grid
        self.grid_columnconfigure(0, weight=3)  # Dashboard takes more space
        self.grid_columnconfigure(1, weight=2)  # Log panel
        self.grid_rowconfigure(1, weight=1)
        
        # Dashboard (left side)
        self.dashboard = Dashboard(
            self,
            process_manager=self.process_manager,
            on_view_logs=self._show_logs
        )
        self.dashboard.grid(row=1, column=0, padx=(10, 5), pady=10, sticky="nsew")
        
        # Log panel (right side)
        self.log_panel = LogPanel(self)
        self.log_panel.grid(row=1, column=1, padx=(5, 10), pady=10, sticky="nsew")
        
        # Status bar at bottom
        self.status_bar = ctk.CTkFrame(self, fg_color=COLORS["mantle"], height=25, corner_radius=0)
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky="ew")
        
        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text="Ready",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["subtext"],
            anchor="w"
        )
        self.status_label.pack(side="left", padx=10, pady=3)
    
    def _on_status_changed(self, project_id: int, status: str):
        """Handle project status change."""
        self.after(0, lambda: self.dashboard.update_project_status(project_id, status))
        self.after(0, self._update_status_bar)
    
    def _on_log_received(self, project_id: int, line: str):
        """Handle new log line."""
        self.after(0, lambda: self.log_panel.add_log(project_id, line))
    
    def _on_crash_detected(self, project_id: int, name: str, exit_code: int, logs: str):
        """Handle process crash."""
        def show_crash():
            self.log_panel.set_project(project_id, name)
            self.log_panel.add_log(project_id, f"\n{'='*50}")
            self.log_panel.add_log(project_id, f"⚠️ CRASHED with exit code {exit_code}")
            self.log_panel.add_log(project_id, f"{'='*50}\n")
            messagebox.showwarning(
                "Process Crashed",
                f"'{name}' crashed with exit code {exit_code}"
            )
        self.after(0, show_crash)
    
    def _show_logs(self, project_id: int, project_name: str):
        """Show logs for a project."""
        self.log_panel.set_project(project_id, project_name)
    
    def _update_status_bar(self):
        """Update the status bar."""
        total = self.dashboard.get_project_count()
        running = self.dashboard.get_running_count()
        self.status_label.configure(text=f"Projects: {total} | Running: {running}")
    
    def _on_closing(self):
        """Handle window close - stop all processes."""
        running = self.dashboard.get_running_count()
        
        if running > 0:
            if not messagebox.askyesno(
                "Confirm Exit",
                f"There are {running} running project(s).\nStop them and exit?"
            ):
                return
        
        self.process_manager.stop_all()
        self.destroy()
