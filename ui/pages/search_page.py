"""Search Results Page - fully theme-aware."""
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QSizePolicy, QGridLayout
)

from modules.api.tmdb_api import TMDBError, search
from ui.components.media_card import MediaCard
from ui.components.animation_manager import fade_in
from ui.app_state import theme_state


class _SearchThread(QThread):
    done = Signal(list, str)

    def __init__(self, query: str):
        super().__init__()
        self.query = query

    def run(self) -> None:
        try:
            movies = search("movie", self.query)
            tv = search("tv", self.query)
            for m in movies:
                m["media_type"] = "movie"
            for t in tv:
                t["media_type"] = "tv"
            combined = movies + tv
            combined.sort(key=lambda x: x.get("popularity", 0), reverse=True)
            self.done.emit(combined, "")
        except TMDBError as exc:
            self.done.emit([], str(exc))
        except Exception as exc:
            self.done.emit([], f"Unexpected error: {exc}")


class SearchPage(QWidget):
    open_details = Signal(int, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._thread: _SearchThread | None = None
        self._items: list[dict] = []
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._build_ui()
        self.refresh_theme()

    def _build_ui(self) -> None:
        self.setStyleSheet("background-color: transparent;")
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        self.title_lbl = QLabel("Search Results")
        root.addWidget(self.title_lbl)

        self.status_lbl = QLabel("")
        root.addWidget(self.status_lbl)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("QScrollArea { border:none; background:transparent; }")
        self.scroll.viewport().setStyleSheet("background: transparent;")

        self.grid_host = QWidget()
        self.grid_host.setStyleSheet("background: transparent;")
        self.grid = QGridLayout(self.grid_host)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(14)
        self.grid.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.scroll.setWidget(self.grid_host)
        root.addWidget(self.scroll, 1)

    def load_query(self, query: str) -> None:
        self.title_lbl.setText(f"Search Results for: '{query}'")
        self.status_lbl.setText("Searching...")
        self._items = []

        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._thread = _SearchThread(query)
        self._thread.done.connect(self._on_results)
        self._thread.start()
        fade_in(self, 220)

    def _on_results(self, items: list, error: str) -> None:
        if error:
            self.status_lbl.setText(f"Error: {error}")
            return
        if not items:
            self.status_lbl.setText("No results found. Try a different search term.")
            return

        self.status_lbl.setText(f"Found {len(items)} results")
        self._items = items
        self._populate_grid()

    def _populate_grid(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        width = self.scroll.viewport().width()
        if width <= 0:
            width = 1000

        cols = max(1, (width + 14) // 194)

        for i, item in enumerate(self._items):
            media_type = item.get("media_type", "movie")
            card = MediaCard(item, media_type)
            card.clicked.connect(
                lambda tid, mt=media_type: self.open_details.emit(tid, mt)
            )
            row = i // cols
            col = i % cols
            self.grid.addWidget(card, row, col)

        for c in range(cols):
            self.grid.setColumnStretch(c, 1)
        for c in range(cols, 15):
            self.grid.setColumnStretch(c, 0)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        try:
            if not self._items:
                return
            width = self.scroll.viewport().width()
            if width <= 0:
                return

            cols = max(1, (width + 14) // 194)

            current_cols = 1
            if self.grid.count() > 0:
                current_cols = 0
                for c in range(15):
                    if self.grid.columnStretch(c) > 0:
                        current_cols += 1

            if cols != current_cols:
                self._populate_grid()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # THEME REFRESH
    # ------------------------------------------------------------------
    def refresh_theme(self) -> None:
        """Called by MainWindow when the theme changes."""
        self.title_lbl.setStyleSheet(
            f"color:{theme_state.text()}; font-size:24px; font-weight:700;"
            f"background:transparent; border: none;"
        )
        self.status_lbl.setStyleSheet(
            f"color:{theme_state.text_dim()}; font-size:12px;"
            f"background:transparent; border: none;"
        )

        # Repaint existing cards so they flip theme colors instantly
        for i in range(self.grid.count()):
            w = self.grid.itemAt(i).widget()
            if w and hasattr(w, "refresh_theme"):
                try:
                    w.refresh_theme()
                except Exception:
                    pass