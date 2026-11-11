"""User Dashboard (Home): Hero carousel + Recently Added sections."""
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtWidgets import (
    QLabel, QVBoxLayout, QWidget, QScrollArea, QGridLayout
)

from modules.api.tmdb_api import get_popular
from ui.components.media_card import MediaCard
from ui.components.hero_section import HeroSection
from ui.components.workers import run_async
from ui.components.animation_manager import fade_in
from config.settings import COLOR_TEXT, COLOR_TEXT_DIM

class HomePage(QWidget):
    open_details = Signal(int, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._all_items = []
        self._grid = None
        self._hero_loading = False
        self._has_loaded = False
        
        # Timer for resizing (prevents crash)
        self._resize_timer = QTimer(self)
        self._resize_timer.setSingleShot(True)
        self._resize_timer.timeout.connect(self._populate_grid)
        
        self._build_ui()

    def _build_ui(self) -> None:
        self.setStyleSheet("background-color: transparent;")
        
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("QScrollArea { border:none; background:transparent; }")
        self.scroll.viewport().setStyleSheet("background: transparent;")
        
        self.content = QWidget()
        self.content.setStyleSheet("background: transparent;")
        self.body = QVBoxLayout(self.content)
        self.body.setContentsMargins(24, 20, 24, 20)
        self.body.setSpacing(20)

        self.welcome = QLabel("Welcome back!")
        self.welcome.setStyleSheet(f"color: {COLOR_TEXT}; font-size: 26px; font-weight: 800;")
        self.body.addWidget(self.welcome)
        
        self.hero = HeroSection()
        self.hero.open_details.connect(self.open_details.emit)
        self.body.addWidget(self.hero)
        
        self.sections_layout = QVBoxLayout()
        self.sections_layout.setSpacing(22)
        self.body.addLayout(self.sections_layout)
        self.body.addStretch(1)
        
        self.scroll.setWidget(self.content)
        root.addWidget(self.scroll)

    def reload(self) -> None:
        """Called when the user opens the Home page."""
        fade_in(self, 220)
        
        # If we already loaded data, don't reload (fixes delay when clicking back to Home)
        if self._has_loaded:
            return
            
        self._has_loaded = True
        
        # Delay by 100ms so the UI appears instantly before fetching
        QTimer.singleShot(100, self._start_fetching)

    def _start_fetching(self):
        self._load_hero()
        self._build_sections()

    def _load_hero(self) -> None:
        if self._hero_loading: return
        self._hero_loading = True
        run_async(get_popular, "movie", on_done=self._hero_done, on_error=self._hero_failed)

    def _hero_done(self, items) -> None:
        self._hero_loading = False
        self.hero.set_items(items[:5])

    def _hero_failed(self, exc) -> None:
        self._hero_loading = False
        self.hero.set_items([])

    def _build_sections(self) -> None:
        # Clear existing
        while self.sections_layout.count():
            item = self.sections_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    sub = item.layout().takeAt(0)
                    if sub.widget():
                        sub.widget().deleteLater()

        # Fetch Trending Movies
        run_async(get_popular, "movie", on_done=self._on_movies_loaded, on_error=lambda e: None)

    def _on_movies_loaded(self, items: list):
        if not items: return
        
        self._all_items = items[:12]
        
        box = QWidget()
        lay = QVBoxLayout(box)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)
        
        header_box = QWidget()
        header_lay = QVBoxLayout(header_box)
        header_lay.setContentsMargins(0, 0, 0, 0)
        header_lay.setSpacing(2)
        
        t = QLabel("Trending Movies")
        t.setStyleSheet(f"color: {COLOR_TEXT}; font-size: 18px; font-weight: 700;")
        header_lay.addWidget(t)
        
        s = QLabel("Popular right now")
        s.setStyleSheet(f"color: {COLOR_TEXT_DIM}; font-size: 12px;")
        header_lay.addWidget(s)
            
        lay.addWidget(header_box)
        
        self.grid_widget = QWidget()
        self._grid = QGridLayout(self.grid_widget)
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setSpacing(14)
        self._grid.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        lay.addWidget(self.grid_widget)
        self.sections_layout.addWidget(box)

        # Build the cards immediately
        self._populate_grid()

    def _populate_grid(self):
        try:
            if not self._grid or not self._all_items:
                return
                
            # Clear existing cards
            while self._grid.count():
                item = self._grid.takeAt(0)
                if item.widget(): 
                    item.widget().deleteLater()

            # Calculate columns
            width = self.scroll.viewport().width() - 48 
            if width < 200: width = 1000 
            cols = max(1, (width + 14) // 194) 

            for i, m in enumerate(self._all_items):
                card = MediaCard(m, "movie")
                card.clicked.connect(lambda tid=m["id"]: self.open_details.emit(tid, "movie"))
                row = i // cols
                col = i % cols
                self._grid.addWidget(card, row, col)
                
            # Stretch columns to fill space
            for c in range(cols):
                self._grid.setColumnStretch(c, 1)
        except Exception:
            pass

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._resize_timer.start(150) 

    def on_hide(self) -> None:
        if hasattr(self.hero, "timer"):
            self.hero.timer.stop()