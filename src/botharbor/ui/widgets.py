"""Shared UI widgets."""

from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve

class ActionButton(QPushButton):
    """Compact action button with text label and hover animation."""
    
    def __init__(self, text: str = "", tooltip: str = "", parent=None):
        super().__init__(text, parent)
        self.setToolTip(tooltip)
        self.setFixedHeight(32)
        self.setMinimumWidth(32)
        self.setIconSize(QSize(20, 20))
        self.setCursor(Qt.PointingHandCursor)
        
        # Styles are handled in QSS (ActionButton selector)
        
        font = self.font()
        font.setPointSize(10)
        self.setFont(font)
        
    def enterEvent(self, event):
        """Scale up icon on hover."""
        self._animate_icon(QSize(24, 24))
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Scale down icon on leave."""
        self._animate_icon(QSize(20, 20))
        super().leaveEvent(event)

    def _animate_icon(self, target_size: QSize):
        """Animate the icon size property."""
        anim = QPropertyAnimation(self, b"iconSize", self)
        anim.setDuration(100)  # Fast 100ms animation
        anim.setStartValue(self.iconSize())
        anim.setEndValue(target_size)
        anim.setEasingCurve(QEasingCurve.OutQuad)
        anim.start()


class HeaderButton(QPushButton):
    """Header button with hover animation for icon and font size."""
    
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self._base_icon_size = QSize(18, 18)
        self._hover_icon_size = QSize(22, 22)
        self._base_font_size = 12
        self._hover_font_size = 13
        self.setIconSize(self._base_icon_size)
        self.setCursor(Qt.PointingHandCursor)
        self.setProperty("headerButton", True)
        # Use fixed size to completely prevent layout shifts
        self.setFixedHeight(38)
        
        # Set initial font
        font = self.font()
        font.setPointSize(self._base_font_size)
        self.setFont(font)
        
    def enterEvent(self, event):
        """Scale up icon and font on hover."""
        self._animate_icon(self._hover_icon_size)
        self._set_font_size(self._hover_font_size)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Scale down icon and font on leave."""
        self._animate_icon(self._base_icon_size)
        self._set_font_size(self._base_font_size)
        super().leaveEvent(event)
    
    def _set_font_size(self, size: int):
        """Set the font size."""
        font = self.font()
        font.setPointSize(size)
        self.setFont(font)

    def _animate_icon(self, target_size: QSize):
        """Animate the icon size property."""
        anim = QPropertyAnimation(self, b"iconSize", self)
        anim.setDuration(100)
        anim.setStartValue(self.iconSize())
        anim.setEndValue(target_size)
        anim.setEasingCurve(QEasingCurve.OutQuad)
        anim.start()
