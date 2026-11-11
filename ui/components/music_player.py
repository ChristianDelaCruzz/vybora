"""Music player using QMediaPlayer for Audius/Jamendo streams with Dynamic Theme Support."""
from PySide6.QtCore import QUrl, Qt
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider, QFrame, QSizePolicy
)
from ui.components.icon_manager import get_icon
from ui.app_state import theme_state


class MusicPlayer(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._player = QMediaPlayer(self)
        self._audio = QAudioOutput(self)
        self._player.setAudioOutput(self._audio)
        self._audio.setVolume(0.8)

        self._player.errorOccurred.connect(self._on_error)
        self._player.positionChanged.connect(self._on_position)
        self._player.durationChanged.connect(self._on_duration)

        self._build_ui()
        self.refresh_theme()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 12, 20, 12)
        layout.setSpacing(20)

        # Track Info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        info_layout.setContentsMargins(0, 0, 0, 0)
        
        self.title_lbl = QLabel("No track playing")
        self.title_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        self.artist_lbl = QLabel("VyBora Music")
        self.artist_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        info_layout.addWidget(self.title_lbl)
        info_layout.addWidget(self.artist_lbl)
        layout.addLayout(info_layout, 2)

        # Playback Controls
        self.play_btn = QPushButton()
        self.play_btn.setFixedSize(42, 42)
        self.play_btn.setCursor(Qt.PointingHandCursor)
        self.play_btn.clicked.connect(self.toggle_play)
        layout.addWidget(self.play_btn)

        # Progress Bar & Time
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(4)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        
        self.progress = QSlider(Qt.Horizontal)
        self.progress.setRange(0, 100)
        self.progress.sliderMoved.connect(self._player.setPosition)
        
        self.time_lbl = QLabel("0:00 / 0:00")
        self.time_lbl.setAlignment(Qt.AlignCenter)
        
        progress_layout.addWidget(self.progress)
        progress_layout.addWidget(self.time_lbl)
        layout.addLayout(progress_layout, 5)

    def refresh_theme(self):
        bg_color = theme_state.surface()
        text_main = theme_state.text()
        text_sub = theme_state.text_dim()
        icon_color = theme_state.text()
        btn_bg = "#7655EF"
        slider_handle = "#D946EF"

        # FIX: Force border: none; and background-color on labels to remove the ugly white outline
        self.setStyleSheet(
            f"MusicPlayer {{ background-color: {bg_color}; border-radius: 12px; border: 1px solid {theme_state.border()}; }}"
        )

        self.title_lbl.setStyleSheet(f"color: {text_main}; font-weight: 700; font-size: 14px; background: transparent; border: none;")
        self.artist_lbl.setStyleSheet(f"color: {text_sub}; font-size: 12px; background: transparent; border: none;")
        self.time_lbl.setStyleSheet(f"color: {text_sub}; font-size: 11px; background: transparent; border: none;")

        self.play_btn.setStyleSheet(
            f"QPushButton {{ background: {btn_bg}; border-radius: 21px; border: none; }}"
            f"QPushButton:hover {{ background: #6344D4; }}"
        )
        self._update_play_icon(icon_color)

        self.progress.setStyleSheet(f"""
            QSlider {{ background: transparent; border: none; }}
            QSlider::groove:horizontal {{ border: none; height: 4px; background: rgba(128,128,128,0.2); border-radius: 2px; }}
            QSlider::sub-page:horizontal {{ background: {btn_bg}; border-radius: 2px; }}
            QSlider::handle:horizontal {{ background: {slider_handle}; border: none; width: 12px; height: 12px; margin: -4px 0; border-radius: 6px; }}
        """)

    def _update_play_icon(self, color: str):
        if self._player.playbackState() == QMediaPlayer.PlayingState:
            self.play_btn.setIcon(get_icon("player/pause", color, 20))
        else:
            self.play_btn.setIcon(get_icon("player/play", color, 20))

    def play_url(self, url: str, title: str = "", artist: str = "Unknown Artist"):
        if title: self.title_lbl.setText(title)
        if artist: self.artist_lbl.setText(artist)
        self._player.setSource(QUrl(url))
        self._player.play()
        self._update_play_icon(theme_state.text())

    def toggle_play(self):
        if self._player.playbackState() == QMediaPlayer.PlayingState:
            self._player.pause()
        else:
            self._player.play()
        self._update_play_icon(theme_state.text())

    def _on_position(self, pos: int):
        self.progress.setValue(pos)
        self.time_lbl.setText(f"{self._fmt(pos)} / {self._fmt(self._player.duration())}")

    def _on_duration(self, dur: int):
        self.progress.setMaximum(dur)

    def _on_error(self, error, error_string: str):
        self.title_lbl.setText("Playback Error")
        self.artist_lbl.setText(error_string)

    def _fmt(self, ms: int) -> str:
        s = ms // 1000
        return f"{s // 60}:{s % 60:02d}"