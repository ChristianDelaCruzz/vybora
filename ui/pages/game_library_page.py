"""Game Library Page - Theme-aware placeholder."""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame

from ui.app_state import theme_state
from ui.components.icon_manager import get_icon


class GameLibraryPage(QWidget):
    open_details = Signal(int, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: transparent;")

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        self.header = QLabel("Game Library")
        root.addWidget(self.header)

        self.sub = QLabel("Browse your saved and imported games.")
        root.addWidget(self.sub)

        self.empty_box = QFrame()
        self.empty_box.setObjectName("EmptyBox")
        lay = QVBoxLayout(self.empty_box)
        lay.setAlignment(Qt.AlignCenter)
        lay.setSpacing(12)

        self.icon = QLabel()
        self.icon.setAlignment(Qt.AlignCenter)
        self.icon.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(self.icon)

        self.title = QLabel("No games yet")
        self.title.setAlignment(Qt.AlignCenter)
        lay.addWidget(self.title)

        self.desc = QLabel("A new game provider is being integrated. Check back soon.")
        self.desc.setAlignment(Qt.AlignCenter)
        lay.addWidget(self.desc)

        root.addWidget(self.empty_box, 1)

        self.refresh_theme()

    def refresh_theme(self):
        self.header.setStyleSheet(f"color: {theme_state.text()}; font-size: 24px; font-weight: 700; background: transparent; border: none;")
        self.sub.setStyleSheet(f"color: {theme_state.text_dim()}; font-size: 13px; background: transparent; border: none;")

        self.empty_box.setStyleSheet(f"""
            QFrame#EmptyBox {{
                background-color: {theme_state.surface()};
                border-radius: 16px;
                border: 1px solid {theme_state.border()};
            }}
        """)

        self.icon.setPixmap(get_icon("navigation/gamepad-2", theme_state.accent_hex, 64).pixmap(64, 64))
        self.title.setStyleSheet(f"color: {theme_state.text()}; font-size: 22px; font-weight: 800; background: transparent; border: none;")
        self.desc.setStyleSheet(f"color: {theme_state.text_dim()}; font-size: 14px; background: transparent; border: none;")