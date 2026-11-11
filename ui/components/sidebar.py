"""Left-side navigation sidebar with responsive collapse and full routing."""
from PySide6.QtCore import Qt, Signal, QSize, QEasingCurve, QPropertyAnimation
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QFrame, QScrollArea
)
from PySide6.QtGui import QPixmap

from config.settings import PROJECT_ROOT
from ui.components.icon_manager import get_icon
from ui.app_state import theme_state

EXPANDED, COMPACT = 220, 64


class NavButton(QPushButton):
    def __init__(self, key: str, label: str, icon_name: str, parent=None) -> None:
        super().__init__(parent)
        self.key, self.label_text, self.icon_name = key, label, icon_name
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setIconSize(QSize(20, 20))
        self.setMinimumHeight(42)
        self.setAccessibleName(label)
        self.set_compact(False)
        self._restyle()
        self.toggled.connect(lambda _c: self._restyle())

    def _restyle(self) -> None:
        active = self.isChecked()
        
        # Text color based on theme and active state
        if active:
            color = "#100E1B" if theme_state.is_light else "#FFFFFF"
        else:
            color = theme_state.icon_color()
            
        # Re-render the icon with the correct color
        self.setIcon(get_icon(self.icon_name, color, 20))

        if active:
            bg = ("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
                  "stop:0 rgba(118, 85, 239, 60), "
                  "stop:0.6 rgba(118, 85, 239, 0), stop:1 transparent);")
            border = (f"border-left: 3px solid {theme_state.accent_hex}; "
                      f"border-top-right-radius: 8px; border-bottom-right-radius: 8px;")
            padding = "padding-left: 13px;"
        else:
            bg = "background: transparent;"
            border = "border-left: 3px solid transparent; border-radius: 8px;"
            padding = "padding-left: 13px;"

        self.setStyleSheet(f"""
            QPushButton {{ {bg} {border} {padding} color: {color}; font-weight: 600; text-align: left; outline: none; }}
            QPushButton:hover {{ background: {theme_state.accent_rgba}; color: {theme_state.text()}; outline: none; }}
        """)

    def set_compact(self, compact: bool) -> None:
        self.setText("" if compact else "  " + self.label_text.replace("&", "&&"))
        self.setToolTip(self.label_text if compact else "")


class Sidebar(QFrame):
    navigate = Signal(str)
    logout_requested = Signal()
    toggled = Signal(bool)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("sidebar")
        self._compact = False
        self._buttons: dict[str, NavButton] = {}
        self._labels: list[QLabel] = []
        self._admin_buttons: list[NavButton] = []
        self._admin_labels: list[QLabel] = []
        self._admin_visible = False
        self._user_text = ""

        self.setFixedWidth(EXPANDED)

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 18, 14, 14)
        root.setSpacing(4)

        # Logo
        self.logo_layout = QHBoxLayout()
        self.logo_icon = QLabel()
        pixmap_path = PROJECT_ROOT / "assets" / "icons" / "navigation" / "logo.svg"
        if pixmap_path.exists():
            pixmap = QPixmap(str(pixmap_path))
            self.logo_icon.setPixmap(pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo_icon.setStyleSheet("background: transparent; border: none;")
        
        self.logo_text = QLabel("VyBora")
        self.logo_layout.addWidget(self.logo_icon)
        self.logo_layout.addWidget(self.logo_text)
        self.logo_layout.addStretch()
        root.addLayout(self.logo_layout)
        root.addSpacing(16)

        # Nav Scroll Area
        self._nav_host = QWidget()
        self._nav = QVBoxLayout(self._nav_host)
        self._nav.setContentsMargins(0, 0, 0, 0)
        self._nav.setSpacing(4)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(self._nav_host)
        scroll.setStyleSheet("background: transparent;")
        root.addWidget(scroll, 1)

        # Divider
        self.divider = QFrame()
        self.divider.setFixedHeight(1)
        root.addWidget(self.divider)

        # User Card
        self.user_container = QFrame()
        user_lay = QHBoxLayout(self.user_container)
        user_lay.setContentsMargins(10, 8, 10, 8)
        user_lay.setSpacing(10)

        self.user_icon = QLabel()
        self.user_icon.setStyleSheet("background: transparent; border: none;")
        
        self.user_label = QLabel("")
        self.user_label.setStyleSheet("background: transparent; border: none; font-weight: 700; font-size: 13px;")
        
        user_lay.addWidget(self.user_icon)
        user_lay.addWidget(self.user_label)
        user_lay.addStretch()
        
        self.user_container.setVisible(False)
        root.addWidget(self.user_container)
        root.addSpacing(4)

        # Logout
        self.logout_btn = NavButton("logout", "Log out", "navigation/log-out")
        self.logout_btn.setCheckable(False)
        self.logout_btn.clicked.connect(self.logout_requested.emit)
        root.addWidget(self.logout_btn)

        self._animation = QPropertyAnimation(self, b"minimumWidth", self)
        self._animation.setDuration(180)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.valueChanged.connect(lambda v: self.setMaximumWidth(int(v)))

        self.refresh_theme()

    def refresh_theme(self) -> None:
        bg_color = "#F0EEF6" if theme_state.is_light else "#0B0914"
        border_color = "rgba(0,0,0,10)" if theme_state.is_light else "rgba(255,255,255,15)"
        self.setStyleSheet(f"QFrame#sidebar {{ background-color: {bg_color}; border-right: 1px solid {border_color}; }}")
        
        self.logo_text.setStyleSheet(f"color: {theme_state.text()}; font-size: 24px; font-weight: 900; letter-spacing: 1px; background: transparent; border: none;")
        self.divider.setStyleSheet(f"background: {border_color}; border: none;")
        
        self.user_container.setStyleSheet(f"background-color: {theme_state.surface()}; border-radius: 8px; border: 1px solid {border_color};")
        self.user_icon.setPixmap(get_icon("navigation/user-round", theme_state.text(), 18).pixmap(18, 18))
        self.user_label.setStyleSheet(f"color: {theme_state.text()}; font-size: 13px; font-weight: 700; background: transparent; border: none;")
        
        for lab in self._labels + self._admin_labels:
            lab.setStyleSheet(f"color: {theme_state.text_dim()}; font-size: 10px; font-weight: 700; margin-top: 12px; margin-left: 8px; margin-bottom: 2px; background: transparent; border: none;")
            
        # Redraw all buttons so they pick up the new theme icon colors
        for btn in self._buttons.values():
            btn._restyle()
        self.logout_btn._restyle()

    def set_items(self, sections: list[tuple[str, list[tuple[str, str, str]]]]) -> None:
        while self._nav.count():
            item = self._nav.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._buttons.clear()
        self._labels.clear()
        self._admin_buttons.clear()
        self._admin_labels.clear()

        for title, items in sections:
            if title:
                lab = QLabel(title.upper())
                lab.setStyleSheet(
                    f"color: {theme_state.text_dim()}; font-size: 10px; font-weight: 700;"
                    " margin-top: 12px; margin-left: 8px; margin-bottom: 2px; background: transparent; border: none;"
                )
                lab.setVisible(not self._compact)
                self._labels.append(lab)
                self._nav.addWidget(lab)

            for key, label, ic in items:
                b = NavButton(key, label, ic)
                b.set_compact(self._compact)
                b.clicked.connect(lambda _c=False, k=key: self.navigate.emit(k))
                self._buttons[key] = b
                self._nav.addWidget(b)

        self._nav.addStretch(1)

    def set_active(self, key: str) -> None:
        for k, b in self._buttons.items():
            b.setChecked(k == key)

    def set_user(self, username: str, role: str) -> None:
        self._user_text = f"{username} | {role}"
        self.user_label.setText("" if self._compact else self._user_text)
        self.user_label.setToolTip(self._user_text)
        self.user_container.setVisible(not self._compact)

    def clear_user(self) -> None:
        self._user_text = ""
        self.user_label.setText("")
        self.user_label.setToolTip("")
        self.user_container.setVisible(False)
        self.set_active("")

    def show_admin_nav(self) -> None:
        self._admin_visible = True
        for b in self._admin_buttons:
            b.setVisible(True)
        for lab in self._admin_labels:
            lab.setVisible(not self._compact)

    def hide_admin_nav(self) -> None:
        self._admin_visible = False
        for b in self._admin_buttons:
            b.setVisible(False)
        for lab in self._admin_labels:
            lab.setVisible(False)

    def add_admin_item(self, key: str, label: str, icon_name: str, section_title: str = "Admin") -> None:
        lab = QLabel(section_title.upper())
        lab.setStyleSheet(
            f"color: {theme_state.text_dim()}; font-size: 10px; font-weight: 700;"
            " margin-top: 12px; margin-left: 8px; margin-bottom: 2px; background: transparent; border: none;"
        )
        lab.setVisible(self._admin_visible and not self._compact)
        self._admin_labels.append(lab)
        self._nav.insertWidget(self._nav.count() - 1, lab)

        b = NavButton(key, label, icon_name)
        b.set_compact(self._compact)
        b.clicked.connect(lambda _c=False, k=key: self.navigate.emit(k))
        b.setVisible(self._admin_visible)
        self._buttons[key] = b
        self._admin_buttons.append(b)
        self._nav.insertWidget(self._nav.count() - 1, b)

    def is_compact(self) -> bool:
        return self._compact

    def set_compact(self, compact: bool, animate: bool = True) -> None:
        if compact == self._compact:
            return
        self._compact = compact

        for b in [*self._buttons.values(), self.logout_btn]:
            b.set_compact(compact)

        for lab in self._labels:
            lab.setVisible(not compact)
        for lab in self._admin_labels:
            lab.setVisible(self._admin_visible and not compact)

        self.logo_text.setVisible(not compact)
        self.user_container.setVisible(not compact and bool(self._user_text))
        self.logo_layout.setAlignment(Qt.AlignCenter if compact else Qt.AlignLeft)

        target = COMPACT if compact else EXPANDED
        if animate and self.isVisible():
            self._animation.stop()
            self._animation.setStartValue(self.width())
            self._animation.setEndValue(target)
            self._animation.start()
        else:
            self.setMinimumWidth(target)
            self.setMaximumWidth(target)

        self.toggled.emit(compact)

    def expand(self) -> None:
        self.set_compact(False)

    def collapse(self) -> None:
        self.set_compact(True)