"""Admin Dashboard Page - Connected to SQLite."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, QScrollArea
)

from config.settings import COLOR_TEXT, COLOR_TEXT_DIM, COLOR_SURFACE, COLOR_PURPLE, COLOR_BLUE, COLOR_PINK
from ui.components.icon_manager import get_icon
from ui.components.workers import run_async
from database import admin_repository

class _StatCard(QFrame):
    def __init__(self, title: str, icon_name: str, color: str):
        super().__init__()
        self.setStyleSheet(
            f"background-color: {COLOR_SURFACE}; border-radius: 12px; border: 1px solid rgba(255,255,255,8);"
        )
        lay = QHBoxLayout(self)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(16)

        # Icon Box
        icon_box = QFrame()
        icon_box.setFixedSize(48, 48)
        icon_box.setStyleSheet(f"background-color: rgba({int(color[1:3],16)}, {int(color[3:5],16)}, {int(color[5:7],16)}, 0.15); border-radius: 10px;")
        icon_lay = QVBoxLayout(icon_box)
        icon_lay.setContentsMargins(0, 0, 0, 0)
        icon = QLabel()
        icon.setPixmap(get_icon(icon_name, color, 24).pixmap(24, 24))
        icon.setAlignment(Qt.AlignCenter)
        icon_lay.addWidget(icon)
        lay.addWidget(icon_box)

        # Text Box
        text_lay = QVBoxLayout()
        text_lay.setSpacing(2)
        
        self.val_lbl = QLabel("...")
        self.val_lbl.setStyleSheet(f"color: {COLOR_TEXT}; font-size: 24px; font-weight: 800; background: transparent;")
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"color: {COLOR_TEXT_DIM}; font-size: 13px; font-weight: 600; background: transparent;")
        
        text_lay.addWidget(self.val_lbl)
        text_lay.addWidget(title_lbl)
        lay.addLayout(text_lay)
        lay.addStretch(1)

    def set_value(self, value: int):
        self.val_lbl.setText(f"{value:,}")

class AdminDashboard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: transparent;")
        
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(20)

        header = QLabel("Admin Dashboard")
        header.setStyleSheet(f"color:{COLOR_TEXT}; font-size:24px; font-weight:700; background:transparent;")
        root.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border:none; background:transparent; }")
        scroll.viewport().setStyleSheet("background: transparent;")

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(content)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(20)

        # Stats Grid
        stats_grid = QGridLayout()
        stats_grid.setSpacing(16)
        
        self.card_users = _StatCard("Total Users", "navigation/user-round", COLOR_PURPLE)
        self.card_movies = _StatCard("Total Movies", "navigation/clapperboard", COLOR_BLUE)
        self.card_games = _StatCard("Active Games", "navigation/gamepad-2", COLOR_PINK)
        self.card_music = _StatCard("Music Tracks", "navigation/music-2", "#34D399")
        
        stats_grid.addWidget(self.card_users, 0, 0)
        stats_grid.addWidget(self.card_movies, 0, 1)
        stats_grid.addWidget(self.card_games, 1, 0)
        stats_grid.addWidget(self.card_music, 1, 1)
        
        lay.addLayout(stats_grid)

        # Recent Activity Panel
        self.activity_panel = QFrame()
        self.activity_panel.setStyleSheet(f"background-color: {COLOR_SURFACE}; border-radius: 12px; border: 1px solid rgba(255,255,255,8);")
        self.a_lay = QVBoxLayout(self.activity_panel)
        self.a_lay.setContentsMargins(20, 20, 20, 20)
        self.a_lay.setSpacing(12)

        a_title = QLabel("Recent Activity")
        a_title.setStyleSheet(f"color: {COLOR_TEXT}; font-size: 16px; font-weight: 700;")
        self.a_lay.addWidget(a_title)

        self.activity_container = QVBoxLayout()
        self.a_lay.addLayout(self.activity_container)

        lay.addWidget(self.activity_panel)
        lay.addStretch(1)

        scroll.setWidget(content)
        root.addWidget(scroll)

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_data()

    def refresh_data(self):
        # Fetch Stats
        run_async(admin_repository.get_dashboard_stats, on_done=self._on_stats_loaded)
        
        # Fetch Activity
        run_async(admin_repository.get_recent_activity, on_done=self._on_activity_loaded)

    def _on_stats_loaded(self, stats: dict):
        self.card_users.set_value(stats.get("users", 0))
        self.card_movies.set_value(stats.get("movies", 0))
        self.card_games.set_value(stats.get("games", 0))
        self.card_music.set_value(stats.get("music", 0))

    def _on_activity_loaded(self, activities: list):
        # Clear existing
        while self.activity_container.count():
            item = self.activity_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    sub = item.layout().takeAt(0)
                    if sub.widget():
                        sub.widget().deleteLater()

        if not activities:
            lbl = QLabel("No recent activity recorded.")
            lbl.setStyleSheet(f"color: {COLOR_TEXT_DIM}; font-size: 13px;")
            self.activity_container.addWidget(lbl)
            return

        for action, created_at in activities:
            row = QHBoxLayout()
            dot = QLabel("•")
            dot.setStyleSheet(f"color: {COLOR_PURPLE}; font-size: 16px; font-weight: 900;")
            t = QLabel(str(action))
            t.setStyleSheet(f"color: {COLOR_TEXT}; font-size: 13px;")
            tm = QLabel(str(created_at))
            tm.setStyleSheet(f"color: {COLOR_TEXT_DIM}; font-size: 11px;")
            
            row.addWidget(dot)
            row.addWidget(t)
            row.addStretch(1)
            row.addWidget(tm)
            self.activity_container.addLayout(row)