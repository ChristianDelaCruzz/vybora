"""Media Details Page: shows a movie or TV show with backdrop, cast, and trailer link."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QPixmap, QPainter, QLinearGradient, QColor, QBrush
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QFrame, QSizePolicy, QPushButton, QDialog
)

from modules.api.tmdb_api import TMDBError, get_details, image_url, get_trailer_key
from ui.components.widgets import GradientButton
from ui.components.icon_manager import get_icon
from ui.components.animation_manager import fade_in
from ui.components.toast import Toast
from ui.app_state import theme_state

try:
    from PySide6.QtWebEngineCore import (
        QWebEngineProfile, QWebEnginePage, QWebEngineUrlRequestInterceptor
    )
    from PySide6.QtWebEngineWidgets import QWebEngineView
    WEB_ENGINE_AVAILABLE = True
except ImportError:
    WEB_ENGINE_AVAILABLE = False

_manager = QNetworkAccessManager()


class _YouTubeReferrerInterceptor(QWebEngineUrlRequestInterceptor):
    """Injects the Referer header required by YouTube to bypass Error 153."""
    def interceptRequest(self, info):
        if "youtube.com" in info.requestUrl().host():
            # YouTube requires a valid HTTPS Referer to allow embedded playback.
            info.setHttpHeader(b"Referer", b"https://www.youtube.com/")


class _Backdrop(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pix: QPixmap | None = None
        self.setMinimumHeight(300)
        self.setMaximumHeight(450)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setStyleSheet("background-color: transparent; border-radius: 16px;")
        self.current_url = None

    def set_source(self, url: str | None) -> None:
        if url == self.current_url:
            return
        self.current_url = url
        self._pix = None
        self.update()

        if not url:
            return

        request = QNetworkRequest(QUrl(url))
        reply = _manager.get(request)

        def on_finished():
            if reply.error() == QNetworkReply.NetworkError.NoError:
                pix = QPixmap()
                pix.loadFromData(reply.readAll().data())
                if self.current_url == url:
                    self._pix = pix
                    self.update()
            reply.deleteLater()

        reply.finished.connect(on_finished)

    def paintEvent(self, _e) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        if self._pix:
            scaled = self._pix.scaled(
                self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
            x = (scaled.width() - self.width()) // 2
            y = (scaled.height() - self.height()) // 2
            p.drawPixmap(0, 0, scaled, x, y, self.width(), self.height())

        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0.0, QColor(16, 14, 27, 0))
        grad.setColorAt(0.5, QColor(16, 14, 27, 120))
        grad.setColorAt(1.0, QColor(16, 14, 27, 255))
        p.fillRect(self.rect(), QBrush(grad))


class _TrailerDialog(QDialog):
    """In-app YouTube trailer player with Referer header injection."""
    def __init__(self, video_key: str, title: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{title} — Trailer")
        self.resize(960, 600)
        self.setStyleSheet(f"background: {theme_state.bg()};")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self._profile = None
        self._page = None
        self._view = None
        self._interceptor = None

        if WEB_ENGINE_AVAILABLE:
            # Off-the-record profile to avoid cache conflicts
            self._profile = QWebEngineProfile(self)

            # Install the interceptor to inject the Referer header
            self._interceptor = _YouTubeReferrerInterceptor(self._profile)
            self._profile.setUrlRequestInterceptor(self._interceptor)

            self._page = QWebEnginePage(self._profile, self)
            self._view = QWebEngineView(self)
            self._view.setPage(self._page)

            # Load the embed URL directly
            embed_url = (
                f"https://www.youtube.com/embed/{video_key}"
                f"?autoplay=1&origin=https://www.youtube.com"
            )
            self._view.setUrl(QUrl(embed_url))
            lay.addWidget(self._view)
        else:
            lbl = QLabel("Embedded video player is not available.\nPlease install PySide6-Addons.")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("color: #EF4444; font-size: 14px; padding: 20px;")
            lay.addWidget(lbl)

    def closeEvent(self, event) -> None:
        """Destroy page and view BEFORE the profile to avoid Qt warnings."""
        try:
            if self._view is not None:
                self._view.stop()
                self._view.setPage(None)
                self._view.setParent(None)
                self._view.deleteLater()
                self._view = None

            if self._page is not None:
                self._page.setParent(None)
                self._page.deleteLater()
                self._page = None

            if self._interceptor is not None:
                self._interceptor.setParent(None)
                self._interceptor.deleteLater()
                self._interceptor = None

            if self._profile is not None:
                self._profile.setParent(None)
                self._profile.deleteLater()
                self._profile = None
        except Exception:
            pass

        super().closeEvent(event)


class MediaDetailsPage(QWidget):
    back_requested = Signal()
    play_requested = Signal(int, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tmdb_id: int = 0
        self._media_type: str = "movie"
        self._title: str = ""
        self._build_ui()
        self.refresh_theme()

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

        top = QHBoxLayout()
        self.back_btn = QPushButton("  Back")
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.setFixedHeight(38)
        self.back_btn.clicked.connect(self.back_requested.emit)
        top.addWidget(self.back_btn)
        top.addStretch(1)
        self.body.addLayout(top)

        self.backdrop = _Backdrop()
        self.body.addWidget(self.backdrop)

        info_row = QHBoxLayout()
        info_row.setSpacing(24)

        self.poster = QLabel()
        self.poster.setFixedSize(220, 330)
        self.poster.setScaledContents(True)
        info_row.addWidget(self.poster, 0, Qt.AlignTop)

        info_col = QVBoxLayout()
        info_col.setSpacing(10)

        self.title_lbl = QLabel("")
        self.title_lbl.setWordWrap(True)
        info_col.addWidget(self.title_lbl)

        self.meta_lbl = QLabel("")
        info_col.addWidget(self.meta_lbl)

        self.desc_lbl = QLabel("")
        self.desc_lbl.setWordWrap(True)
        info_col.addWidget(self.desc_lbl)

        info_col.addSpacing(10)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.play_btn = GradientButton("Play Trailer", "player/play", height=48)
        self.play_btn.setFixedWidth(180)
        self.play_btn.clicked.connect(self._on_play_trailer)
        btn_row.addWidget(self.play_btn)

        self.fav_btn = QPushButton("  Add to Favorites")
        self.fav_btn.setCursor(Qt.PointingHandCursor)
        self.fav_btn.setFixedHeight(48)
        btn_row.addWidget(self.fav_btn)
        btn_row.addStretch(1)

        info_col.addLayout(btn_row)
        info_col.addStretch(1)

        info_row.addLayout(info_col, 1)
        self.body.addLayout(info_row)
        self.body.addStretch(1)

        self.scroll.setWidget(self.content)
        root.addWidget(self.scroll)

    def load(self, media_type: str, tmdb_id: int) -> None:
        self._media_type = media_type
        self._tmdb_id = tmdb_id

        self.title_lbl.setText("Loading...")
        self.meta_lbl.setText("")
        self.desc_lbl.setText("")
        self.poster.clear()
        self.backdrop.set_source(None)

        try:
            data = get_details(media_type, tmdb_id)
        except TMDBError as exc:
            self.title_lbl.setText(f"Error: {exc}")
            return
        except Exception as exc:
            self.title_lbl.setText(f"Unexpected error: {exc}")
            return

        self._title = data.get("title") or data.get("name") or "Untitled"
        self.title_lbl.setText(self._title)

        release = data.get("release_date") or data.get("first_air_date") or ""
        year = release[:4] if release else "—"
        vote = data.get("vote_average")
        rating = f"★ {vote:.1f}" if isinstance(vote, (int, float)) and vote > 0 else "★ —"
        genres = ", ".join(g["name"] for g in data.get("genres", [])) or "—"
        runtime = data.get("runtime") or 0
        runtime_str = f"{runtime} min" if runtime else ""

        self.meta_lbl.setText(f"{year}   {rating}   {genres}   {runtime_str}".strip())
        self.desc_lbl.setText(data.get("overview") or "No description available.")

        poster_url = image_url(data.get("poster_path"), "w342")
        if poster_url:
            req = QNetworkRequest(QUrl(poster_url))
            rep = _manager.get(req)

            def p_done():
                if rep.error() == QNetworkReply.NetworkError.NoError:
                    pix = QPixmap()
                    pix.loadFromData(rep.readAll().data())
                    self.poster.setPixmap(pix)
                rep.deleteLater()

            rep.finished.connect(p_done)

        backdrop_url = image_url(data.get("backdrop_path"), "w1280")
        self.backdrop.set_source(backdrop_url)

        fade_in(self, 250)

    def _on_play_trailer(self):
        if not self._tmdb_id:
            return
        try:
            key = get_trailer_key(self._tmdb_id, self._media_type)
        except Exception as exc:
            Toast(self.window(), "Trailer Error", str(exc), "error").show_toast()
            return

        if not key:
            Toast(self.window(), "No Trailer",
                  "No official trailer is available for this title.", "warning").show_toast()
            return

        if not WEB_ENGINE_AVAILABLE:
            Toast(self.window(), "Player Unavailable",
                  "PySide6-Addons is required for embedded playback.", "error").show_toast()
            return

        dialog = _TrailerDialog(key, self._title, self.window())
        dialog.exec()

    def refresh_theme(self) -> None:
        self.back_btn.setIcon(get_icon("system/arrow-left", theme_state.text(), 16))
        self.back_btn.setStyleSheet(
            f"QPushButton {{ background-color: {theme_state.surface()}; color: {theme_state.text()};"
            f"border: 1px solid {theme_state.border()}; border-radius: 8px; padding: 8px 16px;"
            f"font-weight: 600; }}"
            f"QPushButton:hover {{ background-color: {theme_state.accent_rgba}; }}"
        )

        self.poster.setStyleSheet(
            f"background-color: {theme_state.surface()}; border-radius: 12px;"
            f"border: 1px solid {theme_state.border()};"
        )

        self.title_lbl.setStyleSheet(
            f"color: {theme_state.text()}; font-size: 36px; font-weight: 900; background: transparent;"
        )
        self.meta_lbl.setStyleSheet(
            f"color: {theme_state.text_dim()}; font-size: 14px; font-weight: 600; background: transparent;"
        )
        self.desc_lbl.setStyleSheet(
            f"color: {theme_state.text()}; font-size: 15px; line-height: 1.6; background: transparent;"
        )

        self.fav_btn.setIcon(get_icon("navigation/heart", theme_state.text(), 16))
        self.fav_btn.setStyleSheet(
            f"QPushButton {{ background-color: rgba(255,255,255,8); color: {theme_state.text()};"
            f"border: 1px solid {theme_state.border()}; border-radius: 8px; padding: 0 20px;"
            f"font-weight: 700; }}"
            f"QPushButton:hover {{ background-color: {theme_state.accent_rgba}; "
            f"border: 1px solid {theme_state.accent_hex}; }}"
        )