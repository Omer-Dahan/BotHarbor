"""Add Project dialog for creating new projects."""

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QFileDialog,
    QComboBox, QGroupBox, QMessageBox, QWidget
)

from hamal.core.config import DEFAULT_ENTRY_PATTERNS
from hamal.database.crud import create_project
from hamal.database.models import Project
from hamal.utils.helpers import find_venv_python, IconNames, IconColors
from hamal.ui.widgets import ActionButton
from hamal.ui.icons import get_icon


class AddProjectDialog(QDialog):
    """Dialog for adding a new bot project."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Project")
        self.setMinimumWidth(550)
        self.setModal(True)
        
        self.folder_path: Optional[str] = None
        self.project_name: Optional[str] = None
        self.entry_file: Optional[str] = None
        self.interpreter: Optional[str] = None
        
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Title with icon
        title = QLabel("+ Add New Project")
        title.setObjectName("titleLabel")
        layout.addWidget(title)
        
        subtitle = QLabel("Select a folder containing your Python bot")
        subtitle.setObjectName("subtitleLabel")
        layout.addWidget(subtitle)
        
        layout.addSpacing(8)

        # Folder Selection
        folder_group = QGroupBox("Project Location")
        folder_layout = QHBoxLayout(folder_group)
        
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("Select project folder...")
        self.folder_input.setReadOnly(True)
        folder_layout.addWidget(self.folder_input)
        
        browse_btn = ActionButton("", "Browse Folder")
        browse_btn.setIcon(get_icon(IconNames.MORE, IconColors.TEXT))
        browse_btn.clicked.connect(self._on_browse_folder)
        browse_btn.setProperty("iconButton", True)
        folder_layout.addWidget(browse_btn)
        
        layout.addWidget(folder_group)

        # Project Configuration
        config_group = QGroupBox("Configuration")
        config_layout = QFormLayout(config_group)
        config_layout.setSpacing(12)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter project name")
        # self.name_input.textChanged.connect(self._validate)
        config_layout.addRow("Project Name:", self.name_input)
        
        # Entry file with dropdown and browse button
        entry_widget = QWidget()
        entry_layout = QHBoxLayout(entry_widget)
        entry_layout.setContentsMargins(0, 0, 0, 0)
        entry_layout.setSpacing(8)
        
        self.entry_combo = QComboBox()
        self.entry_combo.setEditable(True)
        # self.entry_combo.currentTextChanged.connect(self._validate)
        entry_layout.addWidget(self.entry_combo)
        
        browse_entry_btn = ActionButton("", "Browse Entry File")
        browse_entry_btn.setIcon(get_icon(IconNames.MORE, IconColors.TEXT))
        browse_entry_btn.clicked.connect(self._on_browse_entry)
        browse_entry_btn.setProperty("iconButton", True)
        entry_layout.addWidget(browse_entry_btn)
        
        config_layout.addRow("Entry File:", entry_widget)
        
        # Interpreter with browse button
        interp_widget = QWidget()
        interp_layout = QHBoxLayout(interp_widget)
        interp_layout.setContentsMargins(0, 0, 0, 0)
        interp_layout.setSpacing(8)
        
        self.interpreter_input = QLineEdit()
        self.interpreter_input.setPlaceholderText("Python interpreter path")
        # self.interpreter_input.textChanged.connect(self._validate)
        interp_layout.addWidget(self.interpreter_input)
        
        browse_interp_btn = ActionButton("", "Browse Interpreter")
        browse_interp_btn.setIcon(get_icon(IconNames.MORE, IconColors.TEXT))
        browse_interp_btn.clicked.connect(self._on_browse_interpreter)
        browse_interp_btn.setProperty("iconButton", True)
        interp_layout.addWidget(browse_interp_btn)
        
        config_layout.addRow("Interpreter:", interp_widget)
        
        layout.addWidget(config_group)

        # Info label
        self.info_label = QLabel("")
        self.info_label.setObjectName("subtitleLabel")
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)
        
        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        self.add_btn = QPushButton("Add Project")
        self.add_btn.setIcon(get_icon(IconNames.PLUS, IconColors.BLUE))
        self.add_btn.setIconSize(QSize(16, 16))
        self.add_btn.setProperty("primary", True)
        self.add_btn.clicked.connect(self._on_add)
        # self.add_btn.setEnabled(False)  # Always enabled for better UX
        button_layout.addWidget(self.add_btn)
        
        layout.addLayout(button_layout)

    def _on_browse_folder(self):
        """Handle folder browse button click."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Project Folder",
            self.folder_path or str(Path.home()),
            QFileDialog.ShowDirsOnly
        )
        
        if folder:
            self._set_folder(folder)

    def _on_browse_entry(self):
        """Browse for entry file."""
        start_dir = self.folder_path if self.folder_path else ""
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Entry File",
            start_dir,
            "Python Files (*.py);;All Files (*)"
        )
        
        if file_path:
            if self.folder_path:
                folder = Path(self.folder_path)
                try:
                    # Try to get relative path
                    rel_path = Path(file_path).relative_to(folder)
                    self.entry_combo.setCurrentText(str(rel_path))
                except ValueError:
                    # File is outside project folder
                    QMessageBox.warning(
                        self,
                        "Invalid Selection",
                        "Entry file must be inside the project folder."
                    )
            else:
                # No folder selected yet, show warning
                QMessageBox.information(
                    self,
                    "Select Folder First",
                    "Please select a project folder first."
                )

    def _on_browse_interpreter(self):
        """Browse for Python interpreter."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Python Interpreter",
            "",
            "Python Executable (python.exe);;All Executables (*.exe)"
        )
        
        if file_path:
            self.interpreter_input.setText(file_path)

    def _set_folder(self, folder: str):
        """Set the selected folder and auto-detect settings."""
        self.folder_path = folder
        self.folder_input.setText(folder)
        
        # Auto-detect project name from folder
        folder_name = Path(folder).name
        self.name_input.setText(folder_name)
        
        # Populate entry file dropdown
        self.entry_combo.clear()
        py_files = get_python_files(folder)
        self.entry_combo.addItems(py_files)
        
        # Auto-select likely entry file
        detected = detect_entry_file(folder)
        info_messages = []
        
        if detected:
            index = self.entry_combo.findText(detected)
            if index >= 0:
                self.entry_combo.setCurrentIndex(index)
                info_messages.append(f"Auto-detected entry file: {detected}")
        elif py_files:
            info_messages.append("No common entry file found. Please select or browse for one.")
        else:
            info_messages.append("No Python files found in this folder.")
        
        # Detect interpreter
        interpreter = detect_python_interpreter(folder)
        self.interpreter_input.setText(interpreter)
        
        if ".venv" in interpreter or "venv" in interpreter:
            info_messages.append("Project venv detected")
        
        self.info_label.setText(" | ".join(info_messages))
        
        # Enable add button if we have required fields
        # self._validate()

    def _validate(self) -> bool:
        """Validate form fields."""
        if not self.folder_path:
             return False
        if not self.name_input.text().strip():
             return False
        if not self.entry_combo.currentText().strip():
             return False
        if not self.interpreter_input.text().strip():
             return False
        return True

    def _on_add(self):
        """Handle add button click."""
        # Check empty fields
        if not self.folder_path:
            QMessageBox.warning(self, "Missing Information", "Please select a project folder.")
            return
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Missing Information", "Please enter a project name.")
            self.name_input.setFocus()
            return
        if not self.entry_combo.currentText().strip():
            QMessageBox.warning(self, "Missing Information", "Please select an entry file.")
            self.entry_combo.setFocus()
            return
        if not self.interpreter_input.text().strip():
            QMessageBox.warning(self, "Missing Information", "Please select a Python interpreter.")
            self.interpreter_input.setFocus()
            return
        
        # Verify entry file exists
        entry_path = Path(self.folder_path) / self.entry_combo.currentText()
        if not entry_path.exists():
            QMessageBox.warning(
                self,
                "Invalid Entry File",
                f"Entry file does not exist:\n{entry_path}"
            )
            return
        
        # Verify interpreter exists
        interpreter_path = Path(self.interpreter_input.text())
        if not interpreter_path.exists():
            QMessageBox.warning(
                self,
                "Invalid Interpreter",
                f"Python interpreter not found:\n{interpreter_path}"
            )
            return
        
        # Store values
        self.project_name = self.name_input.text().strip()
        self.entry_file = self.entry_combo.currentText().strip()
        self.interpreter = self.interpreter_input.text().strip()
        
        self.accept()

    def get_result(self) -> Optional[dict]:
        """Get the dialog result. Returns None if cancelled."""
        if self.result() != QDialog.Accepted:
            return None
        
        return {
            "name": self.project_name,
            "folder_path": self.folder_path,
            "entrypoint": self.entry_file,
            "interpreter_path": self.interpreter,
        }
