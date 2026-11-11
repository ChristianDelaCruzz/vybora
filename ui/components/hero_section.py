"""Cinematic, animated Hero Section carousel."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QPixmap, QPainter, QLinearGradient, QColor, QBrush
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QSizePolicy
)

from config.settings import (
    COLOR_SURFACE, COLOR_TEXT, COLOR_TEXT_DIM,
    COLOR_PURPLE, COLOR_BLUE, COLOR_PINK
)
from modules.api.tmdb_api import image_url
from ui.components.icon_manager import get_icon
from ui.components.widgets import GradientButton
from ui.components.image_cache import ImageLoader

class _HeroBanner(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(420)
        self.setMaximumHeight(500)
        self.setStyleSheet(f"background-color:{COLOR_SURFACE}; border-radius:16px;")
        self.bg_pixmap = None

    def set_image(self, url: str | None) -> None:
        if not url:
            self.bg_pixmap = None
            self.update()
            return

        self.loader = ImageLoader(url)
        self.loader.loaded.connect(self._on_loaded)
        self.loader.start()

    def _on_loaded(self, pix: QPixmap):
        self.bg_pixmap = pix
        self.update()
        self.repaint()

    def paintEvent(self, event):
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()

        if self.bg_pixmap and not self.bg_pixmap.isNull():
            scaled = self.bg_pixmap.scaled(
                self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
            x_offset = (scaled.width() - self.width()) // 2
            y_offset = (scaled.height() - self.height()) // 2
            painter.drawPixmap(0, 0, scaled, x_offset, y_offset, self.width(), self.height())
        else:
            fallback = QLinearGradient(0, 0, self.width(), self.height())
            fallback.setColorAt(0, QColor("#2a1b5e"))
            fallback.setColorAt(0.6, QColor("#1b1440"))
            fallback.setColorAt(1, QColor("#0f2a5c"))
            painter.fillRect(rect, QBrush(fallback))

        gradient_h = QLinearGradient(0, 0, self.width(), 0)
        gradient_h.setColorAt(0.0, QColor(16, 14, 27, 240))
        gradient_h.setColorAt(0.4, QColor(16, 14, 27, 180))
        gradient_h.setColorAt(0.8, QColor(16, 14, 27, 40))
        gradient_h.setColorAt(1.0, QColor(16, 14, 27, 0))
        painter.fillRect(rect, QBrush(gradient_h))

        gradient_v = QLinearGradient(0, self.height(), 0, self.height() * 0.5)
        gradient_v.setColorAt(0.0, QColor(16, 14, 27, 255))
        gradient_v.setColorAt(1.0, QColor(16, 14, 27, 0))
        painter.fillRect(rect, QBrush(gradient_v))


class HeroSection(QWidget):
    open_details = Signal(int, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._items: list[dict] = []
        self._current_index = 0
        
        self._build_ui()
        
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._next_slide)
        self._timer.setInterval(8000)
        self._is_playing = True

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.banner = _HeroBanner()
        banner_layout = QVBoxLayout(self.banner)
        banner_layout.setContentsMargins(50, 50, 50, 40)
        banner_layout.setSpacing(12)

        banner_layout.addStretch(1)

        self.category_lbl = QLabel("TRENDING")
        self.category_lbl.setStyleSheet(
            f"color: {COLOR_PINK}; background-color: rgba(217, 70, 239, 0.15);"
            f"border: 1px solid rgba(217, 70, 239, 0.3); border-radius: 12px;"
            f"padding: 6px 14px; font-size: 11px; font-weight: 900; letter-spacing: 2px;"
        )
        banner_layout.addWidget(self.category_lbl, alignment=Qt.AlignLeft)

        self.title_lbl = QLabel("")
        self.title_lbl.setStyleSheet(
            f"color: {COLOR_TEXT}; font-size: 48px; font-weight: 900; background: transparent; border: none;"
        )
        self.title_lbl.setWordWrap(True)
        banner_layout.addWidget(self.title_lbl)

        self.desc_lbl = QLabel("")
        self.desc_lbl.setStyleSheet(
            f"color: {COLOR_TEXT_DIM}; font-size: 15px; line-height: 1.6; background: transparent; border: none;"
        )
        self.desc_lbl.setWordWrap(True)
        self.desc_lbl.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.desc_lbl.setMaximumWidth(650)
        banner_layout.addWidget(self.desc_lbl)

        banner_layout.addSpacing(10)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(16)

        self.play_btn = GradientButton("Play Trailer", "player/play", height=50)
        self.play_btn.setFixedWidth(180)
        self.play_btn.clicked.connect(self._on_play)
        btn_layout.addWidget(self.play_btn)

        self.details_btn = QPushButton("  View Details")
        self.details_btn.setCursor(Qt.PointingHandCursor)
        self.details_btn.setFixedSize(180, 50)
        self.details_btn.setIcon(get_icon("system/info", COLOR_TEXT, 18))
        self.details_btn.setStyleSheet(
            f"QPushButton {{ background-color: rgba(255, 255, 255, 0.15); color: {COLOR_TEXT};"
            f"border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 8px; font-weight: 700; font-size: 15px; }}"
            f"QPushButton:hover {{ background-color: rgba(255, 255, 255, 0.25); }}"
        )
        self.details_btn.clicked.connect(self._on_details)
        btn_layout.addWidget(self.details_btn)
        
        btn_layout.addStretch(1)
        banner_layout.addLayout(btn_layout)

        banner_layout.addStretch(1)

        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(15)
        
        self.indicator_lbl = QLabel("1 / 5")
        self.indicator_lbl.setStyleSheet(f"color: {COLOR_TEXT}; font-size: 13px; font-weight: 700; background: transparent;")
        bottom_layout.addWidget(self.indicator_lbl)
        
        bottom_layout.addStretch(1)

        controls = QFrame()
        controls.setStyleSheet(
            "background-color: rgba(16, 14, 27, 0.85);" 
            "border: 1px solid rgba(255, 255, 255, 0.2);"
            "border-radius: 20px;"
        )
        controls_layout = QHBoxLayout(controls)
        controls_layout.setContentsMargins(6, 6, 6, 6)
        controls_layout.setSpacing(6)

        btn_style = (
            "QPushButton { background: transparent; border: none; border-radius: 14px; outline: none; }"
            "QPushButton:hover { background: rgba(255, 255, 255, 0.25); }"
        )

        self.prev_btn = QPushButton()
        self.prev_btn.setIcon(get_icon("player/skip-back", "#FFFFFF", 18))
        self.prev_btn.setFixedSize(32, 32)
        self.prev_btn.setCursor(Qt.PointingHandCursor)
        self.prev_btn.setStyleSheet(btn_style)
        self.prev_btn.clicked.connect(self._prev_slide)
        controls_layout.addWidget(self.prev_btn)

        self.pause_btn = QPushButton()
        self.pause_btn.setIcon(get_icon("player/pause", "#FFFFFF", 18))
        self.pause_btn.setFixedSize(32, 32)
        self.pause_btn.setCursor(Qt.PointingHandCursor)
        self.pause_btn.setStyleSheet(btn_style)
        self.pause_btn.clicked.connect(self._toggle_play)
        controls_layout.addWidget(self.pause_btn)

        self.next_btn = QPushButton()
        self.next_btn.setIcon(get_icon("player/skip-forward", "#FFFFFF", 18))
        self.next_btn.setFixedSize(32, 32)
        self.next_btn.setCursor(Qt.PointingHandCursor)
        self.next_btn.setStyleSheet(btn_style)
        self.next_btn.clicked.connect(self._next_slide)
        controls_layout.addWidget(self.next_btn)

        bottom_layout.addWidget(controls)
        banner_layout.addLayout(bottom_layout)
        layout.addWidget(self.banner)

    def set_items(self, items: list[dict]) -> None:
        self._items = items
        self._current_index = 0
        if not self._items:
            self.banner.hide()
            return
        
        self.banner.show()
        self._update_slide()
        self._timer.start()

    def _update_slide(self) -> None:
        if not self._items:
            return
        
        item = self._items[self._current_index]
        media_type = item.get("media_type", "movie")
        
        category = "TRENDING MOVIE" if media_type == "movie" else "TRENDING TV SHOW"
        self.category_lbl.setText(category)
        
        title = item.get("title") or item.get("name") or "Untitled"
        self.title_lbl.setText(title)
        
        desc = item.get("overview") or "No description available."
        if len(desc) > 200:
            desc = desc[:197] + "..."
        self.desc_lbl.setText(desc)
        
        backdrop = image_url(item.get("backdrop_path"), "w1280")
        self.banner.set_image(backdrop)
        
        self.indicator_lbl.setText(f"{self._current_index + 1} / {len(self._items)}")

    def _next_slide(self) -> None:
        if not self._items: return
        self._current_index = (self._current_index + 1) % len(self._items)
        self._update_slide()

    def _prev_slide(self) -> None:
        if not self._items: return
        self._current_index = (self._current_index - 1) % len(self._items)
        self._update_slide()

    def _toggle_play(self) -> None:
        self._is_playing = not self._is_playing
        if self._is_playing:
            self._timer.start()
            self.pause_btn.setIcon(get_icon("player/pause", "#FFFFFF", 18))
        else:
            self._timer.stop()
            self.pause_btn.setIcon(get_icon("player/play", "#FFFFFF", 18))

    def _on_play(self) -> None:
        self._on_details()

    def _on_details(self) -> None:
        if not self._items: return
        item = self._items[self._current_index]
        media_type = item.get("media_type", "movie")
        self.open_details.emit(item["id"], media_type)