"""Icon utilities using SVG icons from Lucide.

Modern, clean SVG icons that scale perfectly at any DPI.
"""

from pathlib import Path
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtCore import QSize, Qt
from PySide6.QtSvg import QSvgRenderer


# Path to icons directory
ICONS_DIR = Path(__file__).parent / "assets" / "icons"


def get_icon(name: str, color: str = "#cdd6f4") -> QIcon:
    """Load SVG icon by name with specified color.
    
    Args:
        name: Icon name without .svg extension (e.g., 'play', 'settings')
        color: Hex color for the icon stroke (default: Catppuccin text color)
    
    Returns:
        QIcon ready for use in buttons/widgets
    """
    icon_path = ICONS_DIR / f"{name}.svg"
    
    if not icon_path.exists():
        # Return empty icon if not found
        return QIcon()
    
    # Read and color the SVG
    svg_content = icon_path.read_text(encoding="utf-8")
    svg_content = svg_content.replace('stroke="currentColor"', f'stroke="{color}"')
    
    # Create icon from colored SVG
    renderer = QSvgRenderer(svg_content.encode())
    
    # Create pixmaps at different sizes for crisp rendering
    icon = QIcon()
    for size in [16, 24, 32, 48]:
        pixmap = QPixmap(QSize(size, size))
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        
        icon.addPixmap(pixmap)
    
    return icon


# Icon name constants for easy access
class IconNames:
    """Available icon names."""
    PLAY = "play"
    STOP = "square"
    SETTINGS = "settings"
    TRASH = "trash"
    FOLDER_OPEN = "folder-open"
    PLUS = "plus"
    ARROW_LEFT = "arrow-left"
    ARROW_RIGHT = "arrow-right"
    MORE = "more-horizontal"


# Catppuccin Mocha colors for icons
class IconColors:
    """Color constants for icons matching the theme."""
    TEXT = "#cdd6f4"
    GREEN = "#a6e3a1"
    RED = "#f38ba8"
    BLUE = "#89b4fa"
    MUTED = "#6c7086"
