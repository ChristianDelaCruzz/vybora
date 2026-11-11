"""Movies & TV Shows browse/search page - fully theme-aware."""
from __future__ import annotations

from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QLabel, QScrollArea, QGridLayout
)

from modules.api.tmdb_api import TMDBError, get_popular, search
from database.media_repository import upsert_many
from ui.components.media_card import MediaCard
from ui.components.animation_manager import fade_in
from ui.components.icon_manager import get_icon
from ui.app_state import theme_state


class _FetchThread(QThread):
    done = Signal(list, str)

    def __init__(self, media_type: str, query: str):
        super().__init__()
        self.media_type = media_type
        self.query = query

    def run(self) -> None:
        try:
            items = (
                search(self.media_type, self.query)
                if self.query else get_popular(self.media_type)
            )
            self.done.emit(items, "")
        except TMDBError as exc:
            self.done.emit([], str(exc))
        except Exception as exc:
            self.done.emit([], f"Unexpected error: {exc}")


class MoviesTvPage(QWidget):
    open_details = Signal(int, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._media_type = "movie"
        self._thread: _FetchThread | None = None
        self._items: list[dict] = []
        
        self._resize_timer = QTimer(self)
        self._resize_timer.setSingleShot(True)
        self._resize_timer.timeout.connect(self._populate_grid)
        
        self._build_ui()
        self.refresh_theme()  # Apply initial theme
        self._load()

    def _build_ui(self) -> None:
        self.setStyleSheet("background-color: transparent;")
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        self.header = QLabel("Movies & TV Shows")
        root.addWidget(self.header)

        search_row = QHBoxLayout()
        search_row.setSpacing(10)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search movies or TV shows...")
        self.search_input.setFixedHeight(42)
        self.search_input.returnPressed.connect(self._on_search)
        search_row.addWidget(self.search_input, 1)

        self.search_btn = QPushButton("  Search")
        self.search_btn.setCursor(Qt.PointingHandCursor)
        self.search_btn.setFixedSize(120, 42)
        self.search_btn.clicked.connect(self._on_search)
        search_row.addWidget(self.search_btn)
        root.addLayout(search_row)

        tabs = QHBoxLayout()
        tabs.setSpacing(8)
        self.movie_tab = self._make_tab("Movies", active=True)
        self.tv_tab = self._make_tab("TV Shows", active=False)
        self.movie_tab.clicked.connect(lambda: self._switch_type("movie"))
        self.tv_tab.clicked.connect(lambda: self._switch_type("tv"))
        tabs.addWidget(self.movie_tab)
        tabs.addWidget(self.tv_tab)
        tabs.addStretch(1)
        root.addLayout(tabs)

        self.status_label = QLabel("")
        root.addWidget(self.status_label)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("QScrollArea { border:none; background:transparent; }")
        self.scroll.viewport().setStyleSheet("background: transparent;")
        
        self.scroll.viewport().installEventFilter(self)

        self.grid_host = QWidget()
        self.grid_host.setStyleSheet("background: transparent;")
        self.grid = QGridLayout(self.grid_host)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(14)
        self.grid.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.scroll.setWidget(self.grid_host)
        root.addWidget(self.scroll, 1)

    def eventFilter(self, obj, event):
        if obj is self.scroll.viewport() and event.type() == event.Type.Resize:
            self._resize_timer.start(100)
        return super().eventFilter(obj, event)

    def _make_tab(self, text: str, active: bool) -> QPushButton:
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(32)
        btn.setStyleSheet(self._tab_style(active))
        return btn

    def _tab_style(self, active: bool) -> str:
        if active:
            return (
                f"QPushButton {{ background-color:{theme_state.accent_hex}; color:white;"
                f"border:none; border-radius:8px; padding:0 16px; font-weight:600; outline: none; }}"
            )
        return (
            f"QPushButton {{ background-color:{theme_state.surface()}; color:{theme_state.text_dim()};"
            f"border:1px solid {theme_state.border()}; border-radius:8px; padding:0 16px; outline: none; }}"
            f"QPushButton:hover {{ color:{theme_state.text()}; border:1px solid {theme_state.accent_hex}; }}"
        )

    def _switch_type(self, media_type: str) -> None:
        if media_type == self._media_type:
            return
        self._media_type = media_type
        self.movie_tab.setStyleSheet(self._tab_style(media_type == "movie"))
        self.tv_tab.setStyleSheet(self._tab_style(media_type == "tv"))
        self.search_input.clear()
        self._load()

    def _on_search(self) -> None:
        self._load(self.search_input.text().strip())

    def _load(self, query: str = "") -> None:
        self._items = []
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        self.status_label.setText("Loading...")
        self._thread = _FetchThread(self._media_type, query)
        self._thread.done.connect(self._on_results)
        self._thread.start()

    def _on_results(self, items: list, error: str) -> None:
        if error:
            self.status_label.setText(f"Error: {error}")
            return
        if not items:
            self.status_label.setText("No results found.")
            return

        try:
            upsert_many(items, self._media_type)
        except Exception:
            pass

        self.status_label.setText(f"{len(items)} results")
        self._items = items
        QTimer.singleShot(10, self._populate_grid)
        fade_in(self, 220)

    def _populate_grid(self):
        try:
            if not self._items: return
                
            while self.grid.count():
                item = self.grid.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            width = self.scroll.viewport().width()
            if width < 200: width = 800
            cols = max(1, (width + 14) // 194)

            for i, item in enumerate(self._items):
                card = MediaCard(item, self._media_type)
                card.clicked.connect(
                    lambda tid, mt=self._media_type: self.open_details.emit(tid, mt)
                )
                row = i // cols
                col = i % cols
                self.grid.addWidget(card, row, col)
                
            for c in range(cols):
                self.grid.setColumnStretch(c, 1)
            for c in range(cols, 15):
                self.grid.setColumnStretch(c, 0)
        except Exception:
            pass

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._resize_timer.start(150)

    # ------------------------------------------------------------------
    # THEME REFRESH
    # ------------------------------------------------------------------
    def refresh_theme(self) -> None:
        """Called by MainWindow when the theme changes."""
        # Header
        self.header.setStyleSheet(
            f"color:{theme_state.text()}; font-size:24px; font-weight:700; "
            f"background:transparent; border: none;"
        )

        # Search input
        self.search_input.setStyleSheet(
            f"QLineEdit {{ background-color:{theme_state.surface()}; color:{theme_state.text()};"
            f"border:1px solid {theme_state.border()}; border-radius:10px; padding:0 16px;"
            f"font-size:13px; outline: none; }}"
            f"QLineEdit:focus {{ border:1px solid {theme_state.accent_hex}; }}"
        )

        # Search button
        self.search_btn.setStyleSheet(
            f"QPushButton {{ background-color: {theme_state.accent_hex};"
            f"color: white; border: none; border-radius: 10px; font-weight: 700;"
            f"font-size: 14px; outline: none; }}"
            f"QPushButton:hover {{ background-color: {theme_state.accent_hex}; }}"
        )
        self.search_btn.setIcon(get_icon("system/search", "#FFFFFF", 16))

        # Tabs
        self.movie_tab.setStyleSheet(self._tab_style(self._media_type == "movie"))
        self.tv_tab.setStyleSheet(self._tab_style(self._media_type == "tv"))

        # Status label
        self.status_label.setStyleSheet(
            f"color:{theme_state.text_dim()}; font-size:12px; background:transparent; border: none;"
        )

        # Refresh existing MediaCards
        for i in range(self.grid.count()):
            w = self.grid.itemAt(i).widget()
            if w and hasattr(w, "refresh_theme"):
                try:
                    w.refresh_theme()
                except Exception:
                    pass