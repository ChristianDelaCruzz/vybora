"""History Page."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame

from ui.app_state import theme_state
from ui.components.icon_manager import get_icon


class HistoryPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: transparent;")
        
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        self.header = QLabel("Watch History")
        root.addWidget(self.header)

        self.empty_box = QFrame()
        self.empty_box.setObjectName("EmptyBox")
        lay = QVBoxLayout(self.empty_box)
        lay.setAlignment(Qt.AlignCenter)
        lay.setSpacing(12)
        
        self.icon = QLabel()
        self.icon.setAlignment(Qt.AlignCenter)
        self.icon.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(self.icon)
        
        self.title = QLabel("Nothing here yet")
        self.title.setAlignment(Qt.AlignCenter)
        lay.addWidget(self.title)
        
        self.desc = QLabel("Content you watch or play will appear here.")
        self.desc.setAlignment(Qt.AlignCenter)
        lay.addWidget(self.desc)

        root.addWidget(self.empty_box, 1)
        
        self.refresh_theme()

    def refresh_theme(self) -> None:
        self.header.setStyleSheet(f"color: {theme_state.text()}; font-size: 24px; font-weight: 700; background: transparent; border: none;")
        
        self.empty_box.setStyleSheet(f"""
            QFrame#EmptyBox {{
                background-color: {theme_state.surface()};
                border-radius: 12px;
                border: 1px solid {theme_state.border()};
            }}
        """)
        
        self.icon.setPixmap(get_icon("system/clock", theme_state.text_dim(), 48).pixmap(48, 48))
        
        self.title.setStyleSheet(f"color: {theme_state.text()}; font-size: 20px; font-weight: 700; background: transparent; border: none;")
        self.desc.setStyleSheet(f"color: {theme_state.text_dim()}; font-size: 13px; background: transparent; border: none;")