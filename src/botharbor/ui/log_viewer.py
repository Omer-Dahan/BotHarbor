"""Log viewer widget for displaying project output."""

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit,
    QPushButton, QLabel, QComboBox
)

from botharbor.core.config import get_project_logs_dir
from botharbor.utils.helpers import open_folder_in_explorer


class LogViewer(QWidget):
    """Widget for viewing real-time and historical logs."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_project_id: Optional[int] = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel("Logs")
        self.title_label.setObjectName("titleLabel")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # Log file selector
        self.log_selector = QComboBox()
        self.log_selector.setMinimumWidth(220)
        self.log_selector.currentTextChanged.connect(self._on_log_selected)
        header_layout.addWidget(self.log_selector)
        
        # Open folder button
        self.open_folder_btn = QPushButton("Open Folder")
        self.open_folder_btn.clicked.connect(self._on_open_folder)
        header_layout.addWidget(self.open_folder_btn)
        
        # Clear button
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self._on_clear)
        header_layout.addWidget(self.clear_btn)
        
        layout.addLayout(header_layout)

        # Log text area
        self.log_text = QPlainTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.log_text.setMaximumBlockCount(10000)  # Limit lines for performance
        layout.addWidget(self.log_text)

        # Status bar
        self.status_label = QLabel("Select a project to view logs")
        self.status_label.setObjectName("subtitleLabel")
        layout.addWidget(self.status_label)

    def set_project(self, project_id: int, project_name: str):
        """Set the project to view logs for."""
        self.current_project_id = project_id
        self.title_label.setText(f"Logs - {project_name}")
        self._refresh_log_files()
        self.log_text.clear()
        self.status_label.setText("Live logs will appear when the project is running")

    def _refresh_log_files(self):
        """Refresh the list of available log files."""
        self.log_selector.clear()
        self.log_selector.addItem("● Live", "live")
        
        if self.current_project_id is None:
            return
        
        logs_dir = get_project_logs_dir(self.current_project_id)
        log_files = sorted(logs_dir.glob("*.log"), reverse=True)
        
        for log_file in log_files[:20]:  # Show last 20 files
            self.log_selector.addItem(log_file.name, str(log_file))

    def _on_log_selected(self, text: str):
        """Handle log file selection."""
        data = self.log_selector.currentData()
        if data == "live":
            self.log_text.clear()
            self.status_label.setText("Showing live logs")
        elif data:
            self._load_log_file(Path(data))

    def _load_log_file(self, path: Path):
        """Load a log file into the viewer."""
        try:
            content = path.read_text(encoding="utf-8")
            self.log_text.setPlainText(content)
            self.status_label.setText(f"Loaded: {path.name}")
            # Scroll to bottom
            scrollbar = self.log_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
        except Exception as e:
            self.log_text.setPlainText(f"Error loading log file: {e}")

    def _on_open_folder(self):
        """Open the logs folder in Explorer."""
        if self.current_project_id is None:
            return
        
        logs_dir = get_project_logs_dir(self.current_project_id)
        open_folder_in_explorer(str(logs_dir))

    def _on_clear(self):
        """Clear the log display."""
        self.log_text.clear()

    @Slot(int, str)
    def append_log(self, project_id: int, line: str):
        """Append a log line (called from ProcessManager signal)."""
        # Only append if viewing live for this project
        if project_id != self.current_project_id:
            return
        
        if self.log_selector.currentData() != "live":
            return
        
        self.log_text.appendPlainText(line)

    def is_showing_live(self) -> bool:
        """Check if currently showing live logs."""
        return self.log_selector.currentData() == "live"
