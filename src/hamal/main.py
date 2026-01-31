"""H.A.M.A.L application entry point with CustomTkinter."""

import sys
import customtkinter as ctk

from hamal.database.database import init_database
from hamal.core.config import APP_NAME, APP_VERSION
from hamal.ui.main_window import MainWindow


def main():
    """Main entry point for H.A.M.A.L."""
    # Initialize database
    init_database()
    
    # Configure CustomTkinter appearance
    ctk.set_appearance_mode("dark")  # Dark mode
    ctk.set_default_color_theme("blue")  # Blue accent color
    
    # Create and run application
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
