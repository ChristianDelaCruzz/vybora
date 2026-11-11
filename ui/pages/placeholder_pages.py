"""Placeholder pages for Game Library, Popular Games, and Music & Audio."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame

from config.settings import COLOR_TEXT, COLOR_TEXT_DIM, COLOR_SURFACE
from ui.components.widgets import GradientButton
from ui.components.icon_manager import get_icon

class _BasePlaceholder(QWidget):
    def __init__(self, title: str, subtitle: str, icon_name: str):
        super().__init__()
        self.setStyleSheet("background-color: transparent;")
        
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        header = QLabel(title)
        header.setStyleSheet(f"color:{COLOR_TEXT}; font-size:24px; font-weight:700; background:transparent; border:none;")
        root.addWidget(header)

        sub = QLabel(subtitle)
        sub.setStyleSheet(f"color:{COLOR_TEXT_DIM}; font-size:13px; background:transparent; border:none;")
        root.addWidget(sub)

        empty_box = QFrame()
        empty_box.setStyleSheet(f"background-color: {COLOR_SURFACE}; border-radius: 12px; border: 1px solid rgba(255,255,255,8);")
        lay = QVBoxLayout(empty_box)
        lay.setAlignment(Qt.AlignCenter)
        lay.setSpacing(12)

        icon = QLabel()
        icon.setPixmap(get_icon(icon_name, COLOR_TEXT_DIM, 48).pixmap(48, 48))
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(icon)

        coming_soon = QLabel("Coming Soon")
        coming_soon.setStyleSheet(f"color: {COLOR_TEXT}; font-size: 20px; font-weight: 700; background: transparent; border: none;")
        coming_soon.setAlignment(Qt.AlignCenter)
        lay.addWidget(coming_soon)

        desc = QLabel("This page is currently under construction.")
        desc.setStyleSheet(f"color: {COLOR_TEXT_DIM}; font-size: 13px; background: transparent; border: none;")
        desc.setAlignment(Qt.AlignCenter)
        lay.addWidget(desc)

        root.addWidget(empty_box, 1)


class GameLibraryPage(_BasePlaceholder):
    def __init__(self):
        super().__init__("Game Library", "Browse your saved and imported games.", "navigation/gamepad-2")

class PopularGamesPage(_BasePlaceholder):
    def __init__(self):
        super().__init__("Popular Games", "Trending games from the community.", "dashboard/trending-up")

class MusicAudioPage(_BasePlaceholder):
    def __init__(self):
        super().__init__("Music & Audio", "Listen to your saved playlists and tracks.", "navigation/music-2")