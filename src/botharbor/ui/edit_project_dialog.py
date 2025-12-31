"""Edit Project dialog for modifying existing projects."""

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QFileDialog,
    QComboBox, QGroupBox, QMessageBox, QWidget
)

from botharbor.database.models import Project
from botharbor.database import crud
from botharbor.utils.helpers import detect_python_interpreter, get_python_files
from botharbor.ui.widgets import ActionButton
from botharbor.ui.icons import get_icon, IconNames, IconColors


class EditProjectDialog(QDialog):
    """Dialog for editing an existing project."""

    def __init__(self, project: Project, parent=None):
        super().__init__(parent)
        self.project = project
        self.setWindowTitle(f"Edit Project - {project.name}")
        self.setMinimumWidth(550)
        self.setModal(True)
        
        self._setup_ui()
        self._load_project_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Title
        title = QLabel("⚙ Edit Project")
        title.setObjectName("titleLabel")
        layout.addWidget(title)
        
        layout.addSpacing(8)

        # Project Info
        info_group = QGroupBox("Project Information")
        info_layout = QFormLayout(info_group)
        info_layout.setSpacing(12)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Project name")
        info_layout.addRow("Name:", self.name_input)
        
        # Folder path (read-only with browse button)
        folder_widget = QWidget()
        folder_layout_inner = QHBoxLayout(folder_widget)
        folder_layout_inner.setContentsMargins(0, 0, 0, 0)
        folder_layout_inner.setSpacing(8)
        
        self.folder_input = QLineEdit()
        self.folder_input.setReadOnly(True)
        folder_layout_inner.addWidget(self.folder_input)
        
        browse_folder_btn = ActionButton("", "Browse Folder")
        browse_folder_btn.setIcon(get_icon(IconNames.MORE, IconColors.TEXT))
        browse_folder_btn.clicked.connect(self._on_browse_folder)
        browse_folder_btn.setProperty("iconButton", True)
        folder_layout_inner.addWidget(browse_folder_btn)
        
        info_layout.addRow("Folder:", folder_widget)
        
        layout.addWidget(info_group)

        # Execution Settings
        exec_group = QGroupBox("Execution Settings")
        exec_layout = QFormLayout(exec_group)
        exec_layout.setSpacing(12)
        
        # Entry file with dropdown and browse
        entry_widget = QWidget()
        entry_layout_inner = QHBoxLayout(entry_widget)
        entry_layout_inner.setContentsMargins(0, 0, 0, 0)
        entry_layout_inner.setSpacing(8)
        
        self.entry_combo = QComboBox()
        self.entry_combo.setEditable(True)
        entry_layout_inner.addWidget(self.entry_combo)
        
        browse_entry_btn = ActionButton("", "Browse Entry File")
        browse_entry_btn.setIcon(get_icon(IconNames.MORE, IconColors.TEXT))
        browse_entry_btn.clicked.connect(self._on_browse_entry)
        browse_entry_btn.setProperty("iconButton", True)
        entry_layout_inner.addWidget(browse_entry_btn)
        
        exec_layout.addRow("Entry File:", entry_widget)
        
        # Interpreter with browse
        interp_widget = QWidget()
        interp_layout_inner = QHBoxLayout(interp_widget)
        interp_layout_inner.setContentsMargins(0, 0, 0, 0)
        interp_layout_inner.setSpacing(8)
        
        self.interpreter_input = QLineEdit()
        interp_layout_inner.addWidget(self.interpreter_input)
        
        browse_interp_btn = ActionButton("", "Browse Interpreter")
        browse_interp_btn.setIcon(get_icon(IconNames.MORE, IconColors.TEXT))
        browse_interp_btn.clicked.connect(self._on_browse_interpreter)
        browse_interp_btn.setProperty("iconButton", True)
        interp_layout_inner.addWidget(browse_interp_btn)
        
        detect_btn = QPushButton("Auto")
        detect_btn.setFixedWidth(50)
        detect_btn.setToolTip("Auto-detect interpreter")
        detect_btn.clicked.connect(self._on_detect_interpreter)
        interp_layout_inner.addWidget(detect_btn)
        
        exec_layout.addRow("Interpreter:", interp_widget)
        
        layout.addWidget(exec_group)
        
        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        self.save_btn = QPushButton("Save Changes")
        self.save_btn.setProperty("primary", True)
        self.save_btn.setIcon(get_icon(IconNames.FOLDER_OPEN, IconColors.BLUE)) # Using Save/Folder icon
        self.save_btn.setIconSize(QSize(16, 16))
        self.save_btn.clicked.connect(self._on_save)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)

    def _load_project_data(self):
        """Load current project data into form."""
        self.name_input.setText(self.project.name)
        self.folder_input.setText(self.project.folder_path)
        self.interpreter_input.setText(self.project.interpreter_path)
        
        # Populate entry file dropdown
        self._refresh_entry_files()
        
        # Set current entry file
        index = self.entry_combo.findText(self.project.entrypoint)
        if index >= 0:
            self.entry_combo.setCurrentIndex(index)
        else:
            self.entry_combo.setCurrentText(self.project.entrypoint)

    def _refresh_entry_files(self):
        """Refresh the entry file dropdown."""
        self.entry_combo.clear()
        if self.folder_input.text():
            py_files = get_python_files(self.folder_input.text())
            self.entry_combo.addItems(py_files)

    def _on_browse_folder(self):
        """Browse for project folder."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Project Folder",
            self.folder_input.text(),
            QFileDialog.ShowDirsOnly
        )
        
        if folder:
            self.folder_input.setText(folder)
            self._refresh_entry_files()

    def _on_browse_entry(self):
        """Browse for entry file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Entry File",
            self.folder_input.text(),
            "Python Files (*.py);;All Files (*)"
        )
        
        if file_path:
            folder = Path(self.folder_input.text())
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

    def _on_detect_interpreter(self):
        """Auto-detect interpreter from project folder."""
        if self.folder_input.text():
            interpreter = detect_python_interpreter(self.folder_input.text())
            self.interpreter_input.setText(interpreter)

    def _on_save(self):
        """Save changes to project."""
        name = self.name_input.text().strip()
        folder = self.folder_input.text().strip()
        entry = self.entry_combo.currentText().strip()
        interpreter = self.interpreter_input.text().strip()
        
        # Validation
        if not name:
            QMessageBox.warning(self, "Validation Error", "Project name is required.")
            return
        
        if not folder or not Path(folder).exists():
            QMessageBox.warning(self, "Validation Error", "Valid project folder is required.")
            return
        
        if not entry:
            QMessageBox.warning(self, "Validation Error", "Entry file is required.")
            return
        
        entry_path = Path(folder) / entry
        if not entry_path.exists():
            QMessageBox.warning(
                self, 
                "Validation Error", 
                f"Entry file does not exist:\n{entry_path}"
            )
            return
        
        if not interpreter or not Path(interpreter).exists():
            QMessageBox.warning(
                self, 
                "Validation Error", 
                f"Python interpreter not found:\n{interpreter}"
            )
            return
        
        # Update project
        crud.update_project(
            self.project.id,
            name=name,
            folder_path=folder,
            entrypoint=entry,
            interpreter_path=interpreter
        )
        
        self.accept()
