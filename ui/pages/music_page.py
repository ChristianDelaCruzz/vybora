"""Music & Audio Library: real Audius + Jamendo tracks."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel,
    QScrollArea, QPushButton, QFrame, QSizePolicy
)
from PySide6.QtGui import QPixmap

from config.settings import COLOR_SURFACE, COLOR_TEXT, COLOR_TEXT_DIM, COLOR_PURPLE
from modules.api.providers.music import audius_provider, jamendo_provider
from ui.components.workers import run_async
from ui.components.widgets import GradientButton, CardGrid, section_header
from ui.components.music_player import MusicPlayer
from ui.components.animation_manager import fade_in
from ui.components.toast import Toast


class TrackCard(QFrame):
    play_requested = Signal(str, str, str)  # url, title, artist

    def __init__(self, track: dict, parent=None):
        super().__init__(parent)
        self._track = track
        self.setFixedSize(180, 240)
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("TrackCard")
        self.setStyleSheet("#TrackCard { background-color: transparent; border-radius: 12px; border: 2px solid transparent; }")
        
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        # Artwork
        self.art = QLabel()
        self.art.setFixedSize(180, 180)
        self.art.setStyleSheet("border-radius: 10px; background: #1B1929;")
        self.art.setScaledContents(True)
        artwork_url = track.get("artwork") or track.get("image")
        if artwork_url:
            try:
                import requests
                r = requests.get(artwork_url, timeout=8)
                if r.ok:
                    pix = QPixmap()
                    pix.loadFromData(r.content)
                    self.art.setPixmap(pix.scaled(180, 180, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
            except Exception:
                pass
        lay.addWidget(self.art)

        # Title
        title = track.get("title") or track.get("name") or "Unknown"
        t = QLabel(title)
        t.setWordWrap(False)
        t.setStyleSheet(f"color: {COLOR_TEXT}; font-size: 13px; font-weight: 700;")
        lay.addWidget(t)

        # Artist
        artist = track.get("artist") or "Unknown Artist"
        a = QLabel(artist)
        a.setStyleSheet(f"color: {COLOR_TEXT_DIM}; font-size: 11px;")
        lay.addWidget(a)

    def enterEvent(self, e):
        self.setStyleSheet(f"#TrackCard {{ background-color: rgba(118,85,239,20); border: 2px solid {COLOR_PURPLE}; border-radius: 12px; }}")
        super().enterEvent(e)

    def leaveEvent(self, e):
        self.setStyleSheet("#TrackCard { background-color: transparent; border: 2px solid transparent; border-radius: 12px; }")
        super().leaveEvent(e)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            url = self._track.get("stream_url")
            title = self._track.get("title") or self._track.get("name") or "Unknown"
            artist = self._track.get("artist") or "Unknown Artist"
            if url:
                self.play_requested.emit(url, title, artist)
            else:
                Toast(self.window(), "Unavailable", "This track cannot be streamed.", "warning").show_toast()
        super().mousePressEvent(e)


class MusicPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("background-color: transparent;")
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        # Header
        header = QLabel("Music & Audio")
        header.setStyleSheet(f"color: {COLOR_TEXT}; font-size: 26px; font-weight: 900;")
        root.addWidget(header)

        # Search
        search_row = QHBoxLayout()
        search_row.setSpacing(10)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search songs, artists...")
        self.search_input.setMinimumHeight(42)
        self.search_input.setStyleSheet(
            f"QLineEdit {{ background-color: {COLOR_SURFACE}; color: {COLOR_TEXT};"
            f"border: 1px solid rgba(255,255,255,20); border-radius: 10px; padding: 0 14px; font-size: 14px; }}"
            f"QLineEdit:focus {{ border: 1px solid {COLOR_PURPLE}; }}"
        )
        self.search_input.returnPressed.connect(self._on_search)
        search_row.addWidget(self.search_input, 1)
        self.search_btn = GradientButton("Search", "system/search", height=42)
        self.search_btn.setFixedWidth(120)
        self.search_btn.clicked.connect(self._on_search)
        search_row.addWidget(self.search_btn)
        root.addLayout(search_row)

        self.status = QLabel("")
        self.status.setStyleSheet(f"color: {COLOR_TEXT_DIM}; font-size: 12px;")
        root.addWidget(self.status)

        # Scrollable sections
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.scroll.viewport().setStyleSheet("background: transparent;")

        self.content = QWidget()
        self.content.setStyleSheet("background: transparent;")
        self.sections = QVBoxLayout(self.content)
        self.sections.setContentsMargins(0, 0, 0, 0)
        self.sections.setSpacing(24)
        self.sections.addStretch(1)

        self.scroll.setWidget(self.content)
        root.addWidget(self.scroll, 1)

        # Bottom Player
        self.player = MusicPlayer()
        root.addWidget(self.player)

        # Load popular tracks on start
        self._load_popular()

    def _on_search(self):
        query = self.search_input.text().strip()
        if not query:
            self._load_popular()
            return
        self.status.setText("Searching...")
        self._clear_sections()
        run_async(audius_provider.search_tracks, query,
                  on_done=lambda items: self._show_results("Audius Search", items, "audius"),
                  on_error=lambda e: self._on_error("Audius", e))
        run_async(jamendo_provider.search_tracks, query,
                  on_done=lambda items: self._show_results("Jamendo Search", items, "jamendo"),
                  on_error=lambda e: self._on_error("Jamendo", e))

    def _load_popular(self):
        self.status.setText("Loading popular tracks...")
        self._clear_sections()
        run_async(audius_provider.get_trending_tracks, 20,
                  on_done=lambda items: self._show_results("Trending on Audius", items, "audius"),
                  on_error=lambda e: self._on_error("Audius", e))
        run_async(jamendo_provider.get_popular_tracks, 20,
                  on_done=lambda items: self._show_results("Popular on Jamendo", items, "jamendo"),
                  on_error=lambda e: self._on_error("Jamendo", e))

    def _show_results(self, title: str, items: list, source: str):
        if not items:
            return
        self.status.setText(f"Loaded {len(items)} tracks from {source.capitalize()}")

        box = QWidget()
        lay = QVBoxLayout(box)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)
        lay.addWidget(section_header(title, f"{len(items)} tracks"))

        grid = CardGrid(min_card_width=180, spacing=16)
        cards = []
        for t in items[:18]:
            card = TrackCard(t)
            card.play_requested.connect(self._on_play_requested)
            cards.append(card)
        grid.set_widgets(cards)
        lay.addWidget(grid)

        # Remove trailing stretch when adding
        if self.sections.count() > 0:
            last = self.sections.takeAt(self.sections.count() - 1)
            if last.spacerItem():
                last.spacerItem().changeSize(0, 0)

        self.sections.addWidget(box)
        self.sections.addStretch(1)
        fade_in(self.content, 200)

    def _on_play_requested(self, url: str, title: str, artist: str):
        self.player.play_url(url, title, artist)
        Toast(self.window(), "Now Playing", f"{title} — {artist}", "success").show_toast()

    def _on_error(self, source: str, exc: Exception):
        self.status.setText(f"{source} error: {exc}")

    def _clear_sections(self):
        while self.sections.count():
            item = self.sections.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    sub = item.layout().takeAt(0)
                    if sub.widget():
                        sub.widget().deleteLater()
            elif item.spacerItem():
                pass