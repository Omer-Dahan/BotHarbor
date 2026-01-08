"""BotHarbor application entry point."""

import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QFile, QTextStream

from botharbor.ui.main_window import MainWindow
from botharbor.utils.helpers import resource_path


def load_stylesheet(app: QApplication):
    """Load the application stylesheet."""
    # Use resource_path for packaged app compatibility
    styles_path = resource_path("ui/styles.qss")
    
    if styles_path.exists():
        file = QFile(str(styles_path))
        if file.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(file)
            app.setStyleSheet(stream.readAll())
            file.close()


def main():
    """Main entry point for BotHarbor."""
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("BotHarbor")
    app.setApplicationVersion("0.1.0")
    app.setStyle("Fusion")  # Use Fusion style as base for dark theme
    
    # Load custom stylesheet
    load_stylesheet(app)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
