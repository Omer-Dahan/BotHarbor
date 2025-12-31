"""Icon definitions using Windows Segoe MDL2 Assets font.

Segoe MDL2 Assets is available on Windows 10/11 and contains
hundreds of icons used by Microsoft apps.

Reference: https://docs.microsoft.com/en-us/windows/apps/design/style/segoe-ui-symbol-font
"""

from PySide6.QtGui import QFont, QFontDatabase


# Segoe MDL2 Assets icon codes (Unicode)
class Icons:
    """Icon characters from Segoe MDL2 Assets font."""
    
    # Player controls
    PLAY = "\uE768"           # Play
    STOP = "\uE71A"           # Stop  
    PAUSE = "\uE769"          # Pause
    REFRESH = "\uE72C"        # Refresh/Restart
    
    # Status
    STATUS_CIRCLE = "\uEA3B"  # Filled circle
    CHECKMARK = "\uE73E"      # Checkmark
    ERROR = "\uE783"          # Error X
    WARNING = "\uE7BA"        # Warning
    
    # Actions
    ADD = "\uE710"            # Add/Plus
    DELETE = "\uE74D"         # Delete/Trash
    EDIT = "\uE70F"           # Edit/Pencil
    SETTINGS = "\uE713"       # Settings/Gear
    SAVE = "\uE74E"           # Save
    CANCEL = "\uE711"         # Cancel/X
    
    # Files & Folders
    FOLDER = "\uE8B7"         # Folder
    FOLDER_OPEN = "\uE838"    # Open folder
    FILE = "\uE7C3"           # File
    DOCUMENT = "\uE8A5"       # Document
    
    # Navigation
    BACK = "\uE72B"           # Back arrow
    FORWARD = "\uE72A"        # Forward arrow
    UP = "\uE74A"             # Up arrow
    DOWN = "\uE74B"           # Down arrow
    
    # UI Elements
    MORE = "\uE712"           # More/Ellipsis
    SEARCH = "\uE721"         # Search
    FILTER = "\uE71C"         # Filter
    COPY = "\uE8C8"           # Copy
    
    # Misc
    LOG = "\uE7C4"            # Log/List
    TERMINAL = "\uE756"       # Terminal/Console
    INFO = "\uE946"           # Info
    POWER = "\uE7E8"          # Power
    SUN = "\uE706"            # Sun (light mode)
    MOON = "\uE708"           # Moon (dark mode)


def get_icon_font(size: int = 9) -> QFont:
    """Get the Segoe MDL2 Assets font for icons."""
    font = QFont("Segoe MDL2 Assets", size)
    return font


def get_fluent_icon_font(size: int = 12) -> QFont:
    """Get the Segoe Fluent Icons font (Windows 11)."""
    font = QFont("Segoe Fluent Icons", size)
    # Fallback to MDL2 if Fluent not available
    if not QFontDatabase.hasFamily("Segoe Fluent Icons"):
        font = QFont("Segoe MDL2 Assets", size)
    return font
