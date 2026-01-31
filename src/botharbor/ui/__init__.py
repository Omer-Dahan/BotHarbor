"""UI components package."""

from botharbor.ui.main_window import MainWindow
from botharbor.ui.dashboard import Dashboard
from botharbor.ui.log_panel import LogPanel
from botharbor.ui.dialogs import AddProjectDialog, EditProjectDialog

__all__ = [
    "MainWindow",
    "Dashboard", 
    "LogPanel",
    "AddProjectDialog",
    "EditProjectDialog"
]
