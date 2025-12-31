"""Dashboard widget showing project table."""

from typing import Optional

from PySide6.QtCore import Qt, Signal, Slot, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QHeaderView, QAbstractItemView, QMessageBox
)
from PySide6.QtGui import QFont

from botharbor.core.process_manager import ProcessManager, ProcessStatus
from botharbor.database.models import Project
from botharbor.database import crud
from botharbor.utils.helpers import format_uptime


class ActionButton(QPushButton):
    """Compact action button with text label."""
    
    def __init__(self, text: str, tooltip: str = "", parent=None):
        super().__init__(text, parent)
        self.setToolTip(tooltip)
        self.setFixedHeight(28)
        self.setMinimumWidth(28)
        self.setCursor(Qt.PointingHandCursor)
        font = self.font()
        font.setPointSize(9)
        self.setFont(font)


class Dashboard(QWidget):
    """Main dashboard with project table and controls."""
    
    # Signals
    project_selected = Signal(int, str)  # project_id, project_name
    request_add_project = Signal()
    request_view_logs = Signal(int, str)  # project_id, project_name
    request_edit_project = Signal(int)    # project_id
    request_delete_project = Signal(int)  # project_id

    # Column indices
    COL_NAME = 0
    COL_STATUS = 1
    COL_UPTIME = 2
    COL_ACTIONS = 3

    def __init__(self, process_manager: ProcessManager, parent=None):
        super().__init__(parent)
        self.process_manager = process_manager
        self.projects: list[Project] = []
        
        self._setup_ui()
        self._connect_signals()
        
        # Timer for updating uptime
        self.uptime_timer = QTimer(self)
        self.uptime_timer.timeout.connect(self._update_uptimes)
        self.uptime_timer.start(1000)  # Update every second

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("Projects")
        title.setObjectName("titleLabel")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Top action buttons with text
        self.start_all_btn = QPushButton("► Start All")
        self.start_all_btn.setProperty("success", True)
        self.start_all_btn.clicked.connect(self._on_start_all)
        header_layout.addWidget(self.start_all_btn)
        
        self.stop_all_btn = QPushButton("■ Stop All")
        self.stop_all_btn.setProperty("danger", True)
        self.stop_all_btn.clicked.connect(self._on_stop_all)
        header_layout.addWidget(self.stop_all_btn)
        
        self.add_btn = QPushButton("+ Add Project")
        self.add_btn.setProperty("primary", True)
        self.add_btn.clicked.connect(lambda: self.request_add_project.emit())
        header_layout.addWidget(self.add_btn)
        
        layout.addLayout(header_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Project", "Status", "Uptime", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(self.COL_NAME, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(self.COL_STATUS, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(self.COL_UPTIME, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(self.COL_ACTIONS, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        
        self.table.cellDoubleClicked.connect(self._on_row_double_clicked)
        
        layout.addWidget(self.table)

        # Empty state
        self.empty_label = QLabel("No projects yet. Click 'Add Project' to get started.")
        self.empty_label.setObjectName("subtitleLabel")
        self.empty_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.empty_label)

    def _connect_signals(self):
        """Connect to ProcessManager signals."""
        self.process_manager.status_changed.connect(self._on_status_changed)

    def refresh_projects(self):
        """Refresh the project list from database."""
        self.projects = crud.get_all_projects()
        self._rebuild_table()

    def _rebuild_table(self):
        """Rebuild the table from current projects."""
        self.table.setRowCount(len(self.projects))
        
        for row, project in enumerate(self.projects):
            self._setup_row(row, project)
        
        # Show/hide empty state
        has_projects = len(self.projects) > 0
        self.table.setVisible(has_projects)
        self.empty_label.setVisible(not has_projects)

    def _setup_row(self, row: int, project: Project):
        """Setup a single row in the table."""
        # Name
        name_item = QTableWidgetItem(project.name)
        name_item.setData(Qt.UserRole, project.id)
        name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(row, self.COL_NAME, name_item)
        
        # Status
        status = self.process_manager.get_status(project.id)
        status_item = QTableWidgetItem(self._get_status_display(status))
        status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(row, self.COL_STATUS, status_item)
        
        # Uptime
        uptime = self.process_manager.get_uptime(project.id)
        uptime_text = format_uptime(uptime) if uptime else "-"
        uptime_item = QTableWidgetItem(uptime_text)
        uptime_item.setFlags(uptime_item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(row, self.COL_UPTIME, uptime_item)
        
        # Actions
        actions_widget = self._create_actions_widget(project.id, status)
        self.table.setCellWidget(row, self.COL_ACTIONS, actions_widget)
        
        # Set row height
        self.table.setRowHeight(row, 50)

    def _get_status_display(self, status: ProcessStatus) -> str:
        """Get display text for a status."""
        status_map = {
            ProcessStatus.STOPPED: "● Stopped",
            ProcessStatus.STARTING: "● Starting...",
            ProcessStatus.RUNNING: "● Running",
            ProcessStatus.STOPPING: "● Stopping...",
            ProcessStatus.CRASHED: "● Crashed",
        }
        return status_map.get(status, "● Unknown")

    def _create_actions_widget(self, project_id: int, status: ProcessStatus) -> QWidget:
        """Create the actions widget for a row."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        is_running = status in (ProcessStatus.RUNNING, ProcessStatus.STARTING)
        
        # Start button
        start_btn = ActionButton("►", "Start")
        start_btn.setEnabled(not is_running)
        start_btn.setProperty("success", True)
        start_btn.clicked.connect(lambda checked, pid=project_id: self._on_start_project(pid))
        layout.addWidget(start_btn)
        
        # Stop button
        stop_btn = ActionButton("■", "Stop")
        stop_btn.setEnabled(is_running)
        stop_btn.setProperty("danger", True)
        stop_btn.clicked.connect(lambda checked, pid=project_id: self._on_stop_project(pid))
        layout.addWidget(stop_btn)
        
        # Logs button
        logs_btn = ActionButton("Log", "View Logs")
        logs_btn.clicked.connect(lambda checked, pid=project_id: self._on_view_logs(pid))
        layout.addWidget(logs_btn)
        
        # Settings/Edit button
        edit_btn = ActionButton("⚙", "Settings")
        edit_btn.clicked.connect(lambda checked, pid=project_id: self._on_edit_project(pid))
        layout.addWidget(edit_btn)
        
        # Delete button
        delete_btn = ActionButton("✕", "Delete")
        delete_btn.setProperty("danger", True)
        delete_btn.setEnabled(not is_running)  # Can't delete while running
        delete_btn.clicked.connect(lambda checked, pid=project_id: self._on_delete_project(pid))
        layout.addWidget(delete_btn)
        
        return widget

    def _on_start_project(self, project_id: int):
        """Start a single project."""
        project = crud.get_project_by_id(project_id)
        if project:
            self.process_manager.start_project(project)

    def _on_stop_project(self, project_id: int):
        """Stop a single project."""
        self.process_manager.stop_project(project_id)

    def _on_view_logs(self, project_id: int):
        """View logs for a project."""
        project = crud.get_project_by_id(project_id)
        if project:
            self.request_view_logs.emit(project.id, project.name)

    def _on_edit_project(self, project_id: int):
        """Edit a project."""
        self.request_edit_project.emit(project_id)

    def _on_delete_project(self, project_id: int):
        """Delete a project after confirmation."""
        project = crud.get_project_by_id(project_id)
        if not project:
            return
        
        reply = QMessageBox.question(
            self,
            "Delete Project",
            f"Are you sure you want to delete '{project.name}'?\n\nThis will not delete the actual project files.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            crud.delete_project(project_id)
            self.refresh_projects()

    def _on_start_all(self):
        """Start all stopped projects."""
        for project in self.projects:
            status = self.process_manager.get_status(project.id)
            if status == ProcessStatus.STOPPED or status == ProcessStatus.CRASHED:
                # Reload from DB to get fresh object
                fresh_project = crud.get_project_by_id(project.id)
                if fresh_project:
                    self.process_manager.start_project(fresh_project)

    def _on_stop_all(self):
        """Stop all running projects."""
        self.process_manager.stop_all()

    def _on_row_double_clicked(self, row: int, col: int):
        """Handle double-click on a row."""
        if row < len(self.projects):
            project = self.projects[row]
            self.project_selected.emit(project.id, project.name)

    @Slot(int, str)
    def _on_status_changed(self, project_id: int, status_str: str):
        """Handle status change from ProcessManager."""
        # Find the row for this project and update status
        for row, project in enumerate(self.projects):
            if project.id == project_id:
                status = ProcessStatus(status_str)
                
                # Update status cell
                status_item = QTableWidgetItem(self._get_status_display(status))
                status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, self.COL_STATUS, status_item)
                
                # Recreate actions widget with updated button states
                actions_widget = self._create_actions_widget(project_id, status)
                self.table.setCellWidget(row, self.COL_ACTIONS, actions_widget)
                break

    def _update_uptimes(self):
        """Update uptime display for all running projects."""
        for row, project in enumerate(self.projects):
            uptime = self.process_manager.get_uptime(project.id)
            uptime_text = format_uptime(uptime) if uptime else "-"
            
            uptime_item = self.table.item(row, self.COL_UPTIME)
            if uptime_item:
                uptime_item.setText(uptime_text)

    def get_project_count(self) -> int:
        """Get the total number of projects."""
        return len(self.projects)

    def get_running_count(self) -> int:
        """Get the number of running projects."""
        count = 0
        for project in self.projects:
            if self.process_manager.get_status(project.id) == ProcessStatus.RUNNING:
                count += 1
        return count
