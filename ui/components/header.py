"""Top header: sidebar toggle, global search, notifications and account menu."""
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLineEdit, QMenu, QPushButton, QWidget, QVBoxLayout, QLabel
)
from ui.components.widgets import IconButton
from ui.components.icon_manager import get_icon
from ui.app_state import theme_state


class Header(QFrame):
    search_submitted = Signal(str)
    toggle_sidebar = Signal()
    profile_requested = Signal()
    settings_requested = Signal()
    logout_requested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFixedHeight(64)
        
        row = QHBoxLayout(self)
        row.setContentsMargins(18, 8, 18, 8)
        row.setSpacing(12)
        
        # Menu Button (Uses system/menu.svg)
        self.menu_btn = IconButton("system/menu", "Toggle sidebar", 20)
        self.menu_btn.clicked.connect(self.toggle_sidebar.emit)
        row.addWidget(self.menu_btn)
        
        # Search Bar
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search movies, TV shows...")
        self.search.setClearButtonEnabled(True)
        self.search.setMaximumWidth(520)
        self.search.setMinimumWidth(150)
        self.search.returnPressed.connect(lambda: self.search_submitted.emit(self.search.text().strip()))
        row.addWidget(self.search, 1)
        row.addStretch(1)
        
        # Notification Bell
        self.bell_container = QWidget()
        self.bell_container.setFixedSize(32, 32)
        bell_layout = QVBoxLayout(self.bell_container)
        bell_layout.setContentsMargins(0, 0, 0, 0)
        
        self.bell = IconButton("system/bell", "Notifications", 20)
        self.bell.clicked.connect(self._show_notifications)
        bell_layout.addWidget(self.bell)
        
        self.dot = QLabel(self.bell_container)
        self.dot.setFixedSize(8, 8)
        self.dot.move(20, 4)
        row.addWidget(self.bell_container)
        
        # Profile Dropdown
        self.profile_btn = QPushButton("")
        self.profile_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.profile_btn.setIconSize(QSize(18, 18))
        self.profile_btn.clicked.connect(self._show_account_menu)
        row.addWidget(self.profile_btn)

        self.refresh_theme()

    def refresh_theme(self) -> None:
        border_color = "rgba(0,0,0,10)" if theme_state.is_light else "rgba(255,255,255,10)"
        self.setStyleSheet(f"QFrame {{ background-color: transparent; border-bottom: 1px solid {border_color}; }}")
        
        self.search.setStyleSheet(
            f"QLineEdit {{ background-color: {theme_state.surface()}; border: 1px solid {theme_state.border()};"
            f"border-radius: 10px; padding: 8px 12px; color: {theme_state.text()}; font-size: 13px; }}"
            f"QLineEdit:focus {{ border: 1px solid {theme_state.accent_hex}; background-color: {theme_state.surface()}; }}"
        )
        
        self.dot.setStyleSheet(f"background-color: #EF4444; border-radius: 4px; border: 2px solid {theme_state.bg()};")
        
        self.profile_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; border: none; color: {theme_state.text()};"
            f"font-weight: 600; text-align: left; padding: 6px 12px; border-radius: 8px; }}"
            f"QPushButton:hover {{ background: {theme_state.accent_rgba}; }}"
        )
        
        # FORCE new icons to generate with the correct color
        icon_color = theme_state.icon_color()
        
        self.menu_btn.setIcon(get_icon("system/menu", icon_color, 20))
        self.bell.setIcon(get_icon("system/bell", icon_color, 20))
        
        # If the profile button has a username (e.g. "Chan"), we only update the icon color
        # Otherwise (if empty), update the icon to match the theme
        if self.profile_btn.text().strip():
            self.profile_btn.setIcon(get_icon("navigation/user-round", theme_state.text(), 18))
        else:
            self.profile_btn.setIcon(get_icon("navigation/user-round", icon_color, 18))

    def set_title(self, title: str) -> None:
        pass

    def set_user(self, username: str, role: str) -> None:
        self.profile_btn.setText(f"  {username}")
        # FIX: Explicitly use theme_state.text() so it's white in dark mode and black in light mode
        self.profile_btn.setIcon(get_icon("navigation/user-round", theme_state.text(), 18))
        self.profile_btn.setToolTip(f"{username} ({role})")
        
    def clear_user(self) -> None:
        self.profile_btn.setText("")
        self.profile_btn.setIcon(get_icon("navigation/user-round", theme_state.icon_color(), 18))
        self.profile_btn.setToolTip("")
        self.search.clear()

    def focus_search(self) -> None:
        self.search.setFocus()
        self.search.selectAll()

    def _show_notifications(self) -> None:
        menu = QMenu(self)
        menu.setStyleSheet(
            f"QMenu {{ background-color: {theme_state.surface()}; color: {theme_state.text()};"
            f"border: 1px solid {theme_state.border()}; border-radius: 8px; padding: 6px; }}"
            f"QMenu::item {{ padding: 8px 24px 8px 16px; border-radius: 6px; font-size: 13px; }}"
        )
        menu.addAction("No new notifications")
        menu.exec(self.bell.mapToGlobal(self.bell.rect().bottomLeft()))

    def _show_account_menu(self) -> None:
        menu = QMenu(self)
        menu.setStyleSheet(
            f"QMenu {{ background-color: {theme_state.surface()}; color: {theme_state.text()};"
            f"border: 1px solid {theme_state.border()}; border-radius: 8px; padding: 6px; }}"
            f"QMenu::item {{ padding: 8px 24px 8px 16px; border-radius: 6px; font-weight: 600; font-size: 13px; }}"
            f"QMenu::item:selected {{ background-color: {theme_state.accent_hex}; color: white; }}"
            f"QMenu::separator {{ height: 1px; background: {theme_state.border()}; margin: 6px 0; }}"
        )
        
        # Use theme text color for icons so they're readable in light mode
        txt_color = theme_state.text()
        
        act_profile = menu.addAction(get_icon("navigation/user-round", txt_color, 16), "My Profile")
        act_profile.triggered.connect(self.profile_requested.emit)
        
        act_settings = menu.addAction(get_icon("navigation/settings", txt_color, 16), "Settings")
        act_settings.triggered.connect(self.settings_requested.emit)
        
        menu.addSeparator()
        
        # Logout icon uses the navigation/log-out SVG
        act_logout = menu.addAction(get_icon("navigation/log-out", "#EF4444", 16), "Log out")
        act_logout.triggered.connect(self.logout_requested.emit)
        
        menu.exec(self.profile_btn.mapToGlobal(self.profile_btn.rect().bottomLeft()))