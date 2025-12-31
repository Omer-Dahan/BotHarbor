"""Main application window."""

import sys
from pathlib import Path

from PySide6.QtCore import Qt, Slot, QUrl
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QStatusBar, QMenuBar, QMenu, QMessageBox
)
from PySide6.QtGui import QAction, QResizeEvent, QDesktopServices

from botharbor.core.process_manager import ProcessManager
from botharbor.database.database import init_database
from botharbor.database import crud
from botharbor.ui.dashboard import Dashboard
from botharbor.ui.log_viewer import LogViewer
from botharbor.ui.add_project_dialog import AddProjectDialog
from botharbor.ui.edit_project_dialog import EditProjectDialog
from botharbor.ui.crash_dialog import CrashNotificationDialog


class MainWindow(QMainWindow):
    """Main application window with dashboard and log viewer."""

    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("BotHarbor")
        # Smaller minimum size for responsive layout
        self.setMinimumSize(400, 300)
        self.resize(1200, 700)
        
        # Initialize database
        init_database()
        
        # Create process manager
        self.process_manager = ProcessManager(self)
        
        # Setup UI
        self._setup_menu()
        self._setup_central_widget()
        self._setup_status_bar()
        
        # Connect signals
        self._connect_signals()
        
        # Load projects
        self.dashboard.refresh_projects()
        self._update_status_bar()

    def _setup_menu(self):
        """Setup the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        add_action = QAction("Add Project...", self)
        add_action.setShortcut("Ctrl+N")
        add_action.triggered.connect(self._on_add_project)
        file_menu.addAction(add_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Projects menu
        projects_menu = menubar.addMenu("Projects")
        
        start_all_action = QAction("Start All", self)
        start_all_action.triggered.connect(lambda: self.dashboard._on_start_all())
        projects_menu.addAction(start_all_action)
        
        stop_all_action = QAction("Stop All", self)
        stop_all_action.triggered.connect(lambda: self.dashboard._on_stop_all())
        projects_menu.addAction(stop_all_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About BotHarbor", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _setup_central_widget(self):
        """Setup the main content area."""
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Splitter for dashboard and log viewer - responsive orientation
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Dashboard (main content)
        self.dashboard = Dashboard(self.process_manager)
        self.splitter.addWidget(self.dashboard)
        
        # Log viewer (side panel)
        self.log_viewer = LogViewer()
        self.splitter.addWidget(self.log_viewer)
        
        # Set initial sizes (60% dashboard, 40% logs)
        self.splitter.setSizes([600, 400])
        
        # Allow collapsing the log viewer
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, True)
        
        layout.addWidget(self.splitter)

    def _setup_status_bar(self):
        """Setup the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.project_count_label = QWidget()
        self.status_bar.addPermanentWidget(self.project_count_label)

    def _connect_signals(self):
        """Connect UI signals."""
        # Dashboard signals
        self.dashboard.request_add_project.connect(self._on_add_project)
        self.dashboard.request_view_logs.connect(self._on_view_logs)
        self.dashboard.project_selected.connect(self._on_project_selected)
        self.dashboard.request_edit_project.connect(self._on_edit_project)
        
        # Process manager signals
        self.process_manager.log_received.connect(self.log_viewer.append_log)
        self.process_manager.status_changed.connect(self._on_status_changed)
        self.process_manager.crash_detected.connect(self._on_crash_detected)

    @Slot()
    def _on_add_project(self):
        """Show add project dialog."""
        dialog = AddProjectDialog(self)
        if dialog.exec():
            result = dialog.get_result()
            if result:
                # Create project in database
                project = crud.create_project(
                    name=result["name"],
                    folder_path=result["folder_path"],
                    entrypoint=result["entrypoint"],
                    interpreter_path=result["interpreter_path"]
                )
                
                # Refresh dashboard
                self.dashboard.refresh_projects()
                self._update_status_bar()
                
                self.status_bar.showMessage(f"Added project: {project.name}", 3000)

    @Slot(int, str)
    def _on_view_logs(self, project_id: int, project_name: str):
        """Show logs for a project."""
        self.log_viewer.set_project(project_id, project_name)

    @Slot(int, str)
    def _on_project_selected(self, project_id: int, project_name: str):
        """Handle project selection (double-click)."""
        self.log_viewer.set_project(project_id, project_name)

    @Slot(int)
    def _on_edit_project(self, project_id: int):
        """Show edit project dialog."""
        project = crud.get_project_by_id(project_id)
        if not project:
            return
        
        dialog = EditProjectDialog(project, self)
        if dialog.exec():
            # Refresh dashboard to show changes
            self.dashboard.refresh_projects()
            self.status_bar.showMessage(f"Updated project: {project.name}", 3000)

    @Slot(int, str)
    def _on_status_changed(self, project_id: int, status: str):
        """Handle status change."""
        self._update_status_bar()

    @Slot(int, str, int, str)
    def _on_crash_detected(self, project_id: int, project_name: str, exit_code: int, recent_logs: str):
        """Handle process crash - show notification dialog."""
        dialog = CrashNotificationDialog(project_name, exit_code, recent_logs, self)
        dialog.show()  # Non-blocking

    def _update_status_bar(self):
        """Update status bar with project counts."""
        total = self.dashboard.get_project_count()
        running = self.dashboard.get_running_count()
        self.status_bar.showMessage(f"Projects: {total} | Running: {running}")

    def _show_about(self):
        """Show about dialog."""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("About BotHarbor")
        msg_box.setText(
            "BotHarbor v0.1.0\n\n"
            "A Windows desktop manager for running\n"
            "multiple Python Telegram bots.\n\n"
            "Created by Omer dahan\n"
            "© 2025 BotHarbor Team\n\n"
            "GitHub: https://github.com/Omer-Dahan/BotHarbor"
        )
        msg_box.setStandardButtons(QMessageBox.Ok)
        open_github_btn = msg_box.addButton("Open GitHub", QMessageBox.ActionRole)
        msg_box.exec()
        
        if msg_box.clickedButton() == open_github_btn:
            QDesktopServices.openUrl(QUrl("https://github.com/Omer-Dahan/BotHarbor"))

    def closeEvent(self, event):
        """Handle window close - stop all processes."""
        running = self.dashboard.get_running_count()
        
        if running > 0:
            reply = QMessageBox.question(
                self,
                "Confirm Exit",
                f"There are {running} running project(s).\n"
                "Do you want to stop them and exit?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                event.ignore()
                return
        
        # Stop all processes
        self.process_manager.stop_all()
        event.accept()

    def resizeEvent(self, event: QResizeEvent):
        """Handle window resize - adjust splitter orientation for narrow windows."""
        super().resizeEvent(event)
        
        # Switch to vertical layout when window is narrow (like a smartphone)
        width = event.size().width()
        if width < 700:
            if self.splitter.orientation() != Qt.Vertical:
                self.splitter.setOrientation(Qt.Vertical)
                # Adjust sizes for vertical layout
                self.splitter.setSizes([400, 200])
        else:
            if self.splitter.orientation() != Qt.Horizontal:
                self.splitter.setOrientation(Qt.Horizontal)
                # Restore horizontal sizes
                self.splitter.setSizes([600, 400])
