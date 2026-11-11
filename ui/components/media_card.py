"""Clickable poster card with premium hover effects."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal, QVariantAnimation, QEasingCurve, QRectF
from PySide6.QtGui import QPixmap, QPainter, QLinearGradient, QColor, QBrush, QPen, QPainterPath
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget, QSizePolicy, QGraphicsDropShadowEffect

from config.settings import COLOR_PURPLE, COLOR_TEXT, COLOR_TEXT_DIM
from modules.api.tmdb_api import image_url
from ui.components.image_cache import ImageLoader

class MediaCard(QFrame):
    clicked = Signal(int)

    def __init__(self, item: dict, media_type: str, parent=None):
        super().__init__(parent)
        self._tmdb_id = int(item.get("id", 0))
        self._media_type = media_type

        self.setMinimumWidth(180)
        self.setFixedHeight(310)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("background-color: transparent;")

        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(0)
        self._shadow.setColor(QColor(COLOR_PURPLE))
        self._shadow.setOffset(0, 6)
        self.setGraphicsEffect(self._shadow)

        self._shadow_anim = QVariantAnimation(self, startValue=0.0, endValue=25.0, duration=250)
        self._shadow_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._shadow_anim.valueChanged.connect(lambda v: self._shadow.setBlurRadius(v))

        self._glow_opacity = 0.0
        self._glow_anim = QVariantAnimation(self, startValue=0.0, endValue=1.0, duration=250)
        self._glow_anim.valueChanged.connect(self._on_glow_change)
        self._glow_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._build(item)

    def _build(self, item: dict) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)

        self.poster = QLabel()
        self.poster.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.poster.setScaledContents(True)
        self.poster.setStyleSheet("border-top-left-radius: 10px; border-top-right-radius: 10px;")
        
        self._raw_pix: QPixmap | None = None
        self._load_poster(item.get("poster_path"))
        layout.addWidget(self.poster, 1)

        info = QWidget()
        info.setStyleSheet("background-color: #100E1B; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;")
        info_lay = QVBoxLayout(info)
        info_lay.setContentsMargins(10, 8, 10, 10)
        info_lay.setSpacing(2)
        info_lay.addStretch(1)

        title = item.get("title") or item.get("name") or "Untitled"
        self.title_lbl = QLabel(title)
        self.title_lbl.setWordWrap(False)
        self.title_lbl.setStyleSheet(f"color: {COLOR_TEXT}; font-size: 14px; font-weight: 700; background: transparent;")
        info_lay.addWidget(self.title_lbl)

        release = item.get("release_date") or item.get("first_air_date") or ""
        year = release[:4] if release else "—"
        vote = item.get("vote_average")
        rating = f"★ {vote:.1f}" if isinstance(vote, (int, float)) and vote > 0 else "★ —"
        
        self.meta_lbl = QLabel(f"{year}   {rating}")
        self.meta_lbl.setStyleSheet(f"color: {COLOR_TEXT_DIM}; font-size: 11px; font-weight: 600; background: transparent;")
        info_lay.addWidget(self.meta_lbl)

        layout.addWidget(info, 0)

    def _load_poster(self, path: str | None) -> None:
        url = image_url(path, "w342")
        if not url:
            self._raw_pix = QPixmap(300, 450)
            self._raw_pix.fill(QColor("#1B1929"))
            self._apply_cover()
            return

        self.loader = ImageLoader(url)
        self.loader.loaded.connect(self._on_loaded)
        self.loader.start()

    def _on_loaded(self, pix: QPixmap):
        self._raw_pix = pix
        self._apply_cover()

    def _apply_cover(self) -> None:
        try:
            if not self._raw_pix or self.poster.width() <= 0 or self.poster.height() <= 0:
                return

            scaled = self._raw_pix.scaled(
                self.poster.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
            x = (scaled.width() - self.poster.width()) // 2
            y = (scaled.height() - self.poster.height()) // 2
            cropped = scaled.copy(x, y, self.poster.width(), self.poster.height())

            painter = QPainter(cropped)
            gradient = QLinearGradient(0, cropped.height() * 0.65, 0, cropped.height())
            gradient.setColorAt(0.0, QColor(16, 14, 27, 0))
            gradient.setColorAt(1.0, QColor(16, 14, 27, 255))
            painter.fillRect(0, 0, cropped.width(), cropped.height(), QBrush(gradient))
            painter.end()

            self.poster.setPixmap(cropped)
        except RuntimeError:
            pass

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._apply_cover()

    def _on_glow_change(self, v: float) -> None:
        self._glow_opacity = v
        self.update()

    def enterEvent(self, event):
        self._glow_anim.setDirection(QVariantAnimation.Direction.Forward)
        self._glow_anim.start()
        self._shadow_anim.setDirection(QVariantAnimation.Direction.Forward)
        self._shadow_anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._glow_anim.setDirection(QVariantAnimation.Direction.Backward)
        self._glow_anim.start()
        self._shadow_anim.setDirection(QVariantAnimation.Direction.Backward)
        self._shadow_anim.start()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self._tmdb_id)
        super().mousePressEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self._glow_opacity > 0.0:
            p = QPainter(self)
            p.setRenderHint(QPainter.Antialiasing)
            rect = QRectF(self.rect()).adjusted(1, 1, -1, -1)

            color = QColor(COLOR_PURPLE)
            color.setAlphaF(self._glow_opacity)

            pen = QPen(color, 2)
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)

            path = QPainterPath()
            path.addRoundedRect(rect, 12, 12)
            p.drawPath(path)