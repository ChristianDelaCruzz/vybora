"""Admin Management Pages (Games, Movies, Users, APIs, Logs)."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, 
    QTableWidgetItem, QHeaderView, QFrame, QLineEdit
)

from config.settings import COLOR_TEXT, COLOR_TEXT_DIM, COLOR_SURFACE, COLOR_PURPLE
from ui.components.widgets import GradientButton
from ui.components.workers import run_async
from database import admin_repository

class _BaseAdminTable(QWidget):
    def __init__(self, title: str, headers: list[str], parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: transparent;")
        
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        header = QLabel(title)
        header.setStyleSheet(f"color:{COLOR_TEXT}; font-size:24px; font-weight:700; background:transparent;")
        root.addWidget(header)

        toolbar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        self.search_input.setFixedHeight(40)
        self.search_input.setStyleSheet(
            f"QLineEdit {{ background-color: {COLOR_SURFACE}; color: white; border-radius: 8px; padding: 0 12px; border: 1px solid rgba(255,255,255,20); }}"
        )
        toolbar.addWidget(self.search_input, 1)
        
        add_btn = GradientButton("Add New", "system/plus", height=40)
        add_btn.setFixedWidth(130)
        toolbar.addWidget(add_btn)
        root.addLayout(toolbar)

        panel = QFrame()
        panel.setStyleSheet(f"background-color: {COLOR_SURFACE}; border-radius: 12px; border: 1px solid rgba(255,255,255,8);")
        p_lay = QVBoxLayout(panel)
        p_lay.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget(0, len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet(f"""
            QTableWidget {{ background-color: transparent; border: none; color: {COLOR_TEXT}; }}
            QTableWidget::item {{ padding: 10px; border-bottom: 1px solid rgba(255,255,255,5); }}
            QHeaderView::section {{ background-color: transparent; color: {COLOR_TEXT_DIM}; font-weight: 700; padding: 10px; border: none; }}
        """)
        p_lay.addWidget(self.table)
        root.addWidget(panel, 1)

    def set_rows(self, rows: list[tuple]):
        self.table.setRowCount(0) # Clear existing
        for row_data in rows:
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, val in enumerate(row_data):
                item = QTableWidgetItem(str(val))
                self.table.setItem(row, col, item)


class AdminGamesPage(_BaseAdminTable):
    def __init__(self, parent=None):
        super().__init__("Manage Games", ["ID", "Title", "Genre", "Platform", "Rating"], parent)

    def showEvent(self, event):
        super().showEvent(event)
        # If you add a get_all_games() to admin_repository, call it here:
        # run_async(admin_repository.get_all_games, on_done=self.set_rows)


class AdminMoviesPage(_BaseAdminTable):
    def __init__(self, parent=None):
        super().__init__("Manage Movies", ["ID", "Title", "Year", "Rating", "Status"], parent)

    def showEvent(self, event):
        super().showEvent(event)
        run_async(admin_repository.get_all_movies, on_done=self.set_rows)


class AdminUsersPage(_BaseAdminTable):
    def __init__(self, parent=None):
        super().__init__("Manage Users", ["ID", "Username", "Role", "Joined"], parent)

    def showEvent(self, event):
        super().showEvent(event)
        run_async(admin_repository.get_all_users, on_done=self.set_rows)


class AdminApiPage(_BaseAdminTable):
    def __init__(self, parent=None):
        super().__init__("API Management", ["Service", "Key", "Status", "Last Sync"], parent)
        self.set_rows([
            ("TMDB", "••••••••", "Active", "Just now"),
            ("RAWG", "••••••••", "Active", "2 hours ago"),
            ("YouTube", "••••••••", "Active", "1 day ago"),
        ])


class AdminLogsPage(_BaseAdminTable):
    def __init__(self, parent=None):
        super().__init__("Activity Logs", ["Time", "User", "Action", "Description"], parent)