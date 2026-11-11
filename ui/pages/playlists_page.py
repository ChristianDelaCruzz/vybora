"""Playlists Page."""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, 
    QDialog, QFormLayout, QLineEdit, QPushButton, QTextEdit
)

from ui.app_state import theme_state
from ui.components.widgets import GradientButton
from ui.components.toast import Toast
from ui.components.icon_manager import get_icon


class NewPlaylistDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Playlist")
        self.setFixedSize(400, 320)
        
        self.setStyleSheet(f"QDialog {{ background-color: {theme_state.bg()}; }}")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        title = QLabel("Create Playlist")
        title.setStyleSheet(f"color: {theme_state.text()}; font-size: 18px; font-weight: 800; background: transparent;")
        layout.addWidget(title)
        
        form = QFormLayout()
        form.setSpacing(12)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Weekend Vibes")
        
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Optional description...")
        self.desc_input.setFixedHeight(80)
        
        inp_style = f"""
            QLineEdit, QTextEdit {{
                background-color: {theme_state.surface()};
                color: {theme_state.text()};
                border: 1px solid {theme_state.border()};
                border-radius: 8px;
                padding: 8px 12px;
            }}
            QLineEdit:focus, QTextEdit:focus {{ border: 1px solid {theme_state.accent_hex}; }}
        """
        self.name_input.setStyleSheet(inp_style)
        self.desc_input.setStyleSheet(inp_style)
        
        name_lbl = QLabel("Playlist Name")
        name_lbl.setStyleSheet(f"color: {theme_state.text_dim()}; font-weight: 600; background: transparent;")
        desc_lbl = QLabel("Description")
        desc_lbl.setStyleSheet(f"color: {theme_state.text_dim()}; font-weight: 600; background: transparent;")
        
        form.addRow(name_lbl, self.name_input)
        form.addRow(desc_lbl, self.desc_input)
        
        layout.addLayout(form)
        layout.addStretch(1)
        
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setFixedSize(100, 36)
        cancel_btn.setStyleSheet(f"background-color: {theme_state.surface()}; color: {theme_state.text()}; border: 1px solid {theme_state.border()}; border-radius: 8px;")
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("Create")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setFixedSize(100, 36)
        save_btn.setStyleSheet(f"background-color: {theme_state.accent_hex}; color: white; font-weight: 700; border-radius: 8px;")
        save_btn.clicked.connect(self.accept)
        
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)


class PlaylistsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: transparent;")
        
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        header_row = QHBoxLayout()
        self.header = QLabel("My Playlists")
        header_row.addWidget(self.header)
        header_row.addStretch(1)
        
        self.new_btn = GradientButton("New Playlist", "system/plus")
        self.new_btn.setFixedWidth(150)
        self.new_btn.clicked.connect(self._open_new_playlist_dialog)
        header_row.addWidget(self.new_btn)
        root.addLayout(header_row)

        self.empty_box = QFrame()
        self.empty_box.setObjectName("EmptyBox")
        lay = QVBoxLayout(self.empty_box)
        lay.setAlignment(Qt.AlignCenter)
        lay.setSpacing(12)
        
        self.icon = QLabel()
        self.icon.setAlignment(Qt.AlignCenter)
        self.icon.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(self.icon)
        
        self.title = QLabel("No playlists created")
        self.title.setAlignment(Qt.AlignCenter)
        lay.addWidget(self.title)
        
        self.desc = QLabel("Create a playlist to organize your favorite music.")
        self.desc.setAlignment(Qt.AlignCenter)
        lay.addWidget(self.desc)

        root.addWidget(self.empty_box, 1)
        
        self.refresh_theme()

    def _open_new_playlist_dialog(self):
        dialog = NewPlaylistDialog(self)
        if dialog.exec():
            name = dialog.name_input.text().strip()
            if not name:
                Toast(self.window(), "Error", "Playlist name cannot be empty.", "error").show_toast()
                return
            
            # TODO: Save to database here once you have a playlists table
            # For now, show success
            Toast(self.window(), "Playlist Created", f"'{name}' has been created.", "success").show_toast()

    def refresh_theme(self) -> None:
        self.header.setStyleSheet(f"color: {theme_state.text()}; font-size: 24px; font-weight: 700; background: transparent; border: none;")
        
        self.empty_box.setStyleSheet(f"""
            QFrame#EmptyBox {{
                background-color: {theme_state.surface()};
                border-radius: 12px;
                border: 1px solid {theme_state.border()};
            }}
        """)
        
        self.icon.setPixmap(get_icon("navigation/list-music", theme_state.text_dim(), 48).pixmap(48, 48))
        
        self.title.setStyleSheet(f"color: {theme_state.text()}; font-size: 20px; font-weight: 700; background: transparent; border: none;")
        self.desc.setStyleSheet(f"color: {theme_state.text_dim()}; font-size: 13px; background: transparent; border: none;")