"""Error notification dialog for crash alerts."""

from hamal.ui.icons import Icons
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QPlainTextEdit, QApplication
)


class CrashNotificationDialog(QDialog):
    """Dialog showing crash notification with log copy functionality."""

    def __init__(self, project_name: str, exit_code: int, last_logs: str, parent=None):
        super().__init__(parent)
        self.project_name = project_name
        self.exit_code = exit_code
        self.last_logs = last_logs
        
        self.setWindowTitle("Process Crashed")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        self.setModal(False)  # Non-modal so user can continue working
        
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Header with error icon
        header = QLabel(f"⚠ Process Crashed: {self.project_name}")
        header.setObjectName("titleLabel")
        header.setStyleSheet("color: #f38ba8; font-size: 16px; font-weight: bold;")
        layout.addWidget(header)

        # Exit code info
        exit_info = QLabel(f"Exit code: {self.exit_code}")
        exit_info.setObjectName("subtitleLabel")
        layout.addWidget(exit_info)

        # Log section
        log_label = QLabel("Last log output:")
        layout.addWidget(log_label)

        self.log_text = QPlainTextEdit()
        self.log_text.setPlainText(self.last_logs)
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(200)
        layout.addWidget(self.log_text)

        # Buttons
        button_layout = QHBoxLayout()
        
        copy_btn = QPushButton("Copy Log")
        copy_btn.clicked.connect(self._on_copy_log)
        button_layout.addWidget(copy_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.setProperty("primary", True)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)

    def _on_copy_log(self):
        """Copy log to clipboard."""
        clipboard = QApplication.clipboard()
        full_log = f"Project: {self.project_name}\nExit Code: {self.exit_code}\n\n--- Log Output ---\n{self.last_logs}"
        clipboard.setText(full_log)
        
        # Brief visual feedback
        sender = self.sender()
        if sender:
            original_text = sender.text()
            sender.setText("Copied!")
            # Reset after a short delay using QTimer
            from PySide6.QtCore import QTimer
            QTimer.singleShot(1500, lambda: sender.setText(original_text))
