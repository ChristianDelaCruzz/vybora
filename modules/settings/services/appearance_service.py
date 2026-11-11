"""Single source of truth for VyBora's QSS."""
from __future__ import annotations

from PySide6.QtWidgets import QApplication


def _palette(light: bool, accent_hex: str) -> dict:
    if light:
        return {
            "bg":         "#F5F3FF",
            "bg_alt":     "#EDE8F8",
            "surface":    "#FFFFFF",
            "surface_2":  "#F8F5FF",
            "text":       "#100E1B",
            "text_dim":   "#5B5675",
            "border":     "#D1CCE0",
            "border_soft": "rgba(16, 14, 27, 30)",
            "icon":       "#100E1B",
            "icon_dim":   "#5B5675",
            "hover_bg":   "rgba(118, 85, 239, 20)",
            "scrollbar":  "#D1CCE0",
            "menu_bg":    "#FFFFFF",
            "shadow":     "rgba(16, 14, 27, 30)",
            "accent":     accent_hex,
            "accent_soft": "rgba(118, 85, 239, 30)",
            "accent_text": "#FFFFFF",
        }
    return {
        "bg":         "#100E1B",
        "bg_alt":     "#0B0914",
        "surface":    "#1B1929",
        "surface_2":  "#29263B",
        "text":       "#F5F3FF",
        "text_dim":   "#A5A0B8",
        "border":     "rgba(255, 255, 255, 20)",
        "border_soft": "rgba(255, 255, 255, 8)",
        "icon":       "#F5F3FF",
        "icon_dim":   "#A5A0B8",
        "hover_bg":   "rgba(255, 255, 255, 12)",
        "scrollbar":  "#3B2C59",
        "menu_bg":    "#1B1929",
        "shadow":     "rgba(0, 0, 0, 120)",
        "accent":     accent_hex,
        "accent_soft": "rgba(118, 85, 239, 40)",
        "accent_text": "#FFFFFF",
    }


_QSS = """
QMainWindow, QWidget#root, QWidget#app_container {{
    background-color: {bg};
    color: {text};
}}

QWidget {{
    color: {text};
    font-family: "Segoe UI", "SF Pro Text", sans-serif;
}}

QLabel {{
    background: transparent;
    color: {text};
    border: none;
}}

QLabel#Muted {{
    color: {text_dim};
}}

QLabel#PageTitle {{
    color: {text};
    font-size: 26px;
    font-weight: 800;
}}

QLabel#SectionTitle {{
    color: {text};
    font-size: 18px;
    font-weight: 700;
}}

QLabel#SectionSubtitle {{
    color: {text_dim};
    font-size: 12px;
}}

QFrame {{
    background: transparent;
    border: none;
}}

QFrame#Sidebar {{
    background-color: {surface};
    border-right: 1px solid {border};
}}

QFrame#Header {{
    background-color: {surface};
    border-bottom: 1px solid {border};
}}

QFrame#CardInfo {{
    background-color: {bg};
    border-bottom-left-radius: 10px;
    border-bottom-right-radius: 10px;
}}

QFrame#UserCard {{
    background-color: {surface_2};
    border: 1px solid {border_soft};
    border-radius: 8px;
}}

QFrame#StatCard {{
    background-color: {surface_2};
    border-radius: 12px;
    border: 1px solid {border_soft};
}}

QPushButton {{
    background-color: {surface_2};
    color: {text};
    border: 1px solid {border};
    border-radius: 8px;
    padding: 8px 14px;
    font-weight: 600;
}}

QPushButton:hover {{
    background-color: {hover_bg};
    border-color: {accent};
}}

QPushButton:pressed {{
    background-color: {accent_soft};
}}

QPushButton#SecondaryButton {{
    background-color: transparent;
    color: {text};
    border: 1px solid {border};
    border-radius: 8px;
    padding: 0 16px;
    font-weight: 600;
    font-size: 13px;
}}

QPushButton#SecondaryButton:hover {{
    border-color: {accent};
    background-color: {hover_bg};
}}

QPushButton#SecondaryButton[variant="danger"]:hover {{
    border-color: #EF4444;
    background-color: rgba(239, 68, 68, 20);
}}

QPushButton#IconButton {{
    background-color: transparent;
    border: none;
    border-radius: 16px;
    padding: 0;
}}

QPushButton#IconButton[hover="true"] {{
    background-color: {hover_bg};
}}

QPushButton#IconButton[pressed="true"] {{
    background-color: {accent_soft};
}}

QPushButton#NavButton {{
    background-color: transparent;
    color: {text_dim};
    border: none;
    border-left: 3px solid transparent;
    border-top-right-radius: 8px;
    border-bottom-right-radius: 8px;
    padding-left: 11px;
    text-align: left;
    font-weight: 600;
    font-size: 13px;
}}

QPushButton#NavButton:hover {{
    background-color: {hover_bg};
    color: {text};
}}

QPushButton#NavButton[active="true"] {{
    background-color: {accent_soft};
    color: {text};
    border-left: 3px solid {accent};
}}

QPushButton#ProfileButton {{
    background: transparent;
    border: none;
    color: {text};
    font-weight: 600;
    text-align: left;
    padding: 6px 12px;
    border-radius: 8px;
}}

QPushButton#ProfileButton:hover {{
    background-color: {hover_bg};
}}

QLineEdit {{
    background-color: {bg_alt};
    color: {text};
    border: 1px solid {border};
    border-radius: 8px;
    padding: 8px 12px;
    selection-background-color: {accent};
    selection-color: {accent_text};
}}

QLineEdit:focus {{
    border: 1px solid {accent};
}}

QLineEdit#HeaderSearch {{
    border-radius: 10px;
    padding: 8px 12px;
}}

QComboBox, QSpinBox, QDoubleSpinBox {{
    background-color: {bg_alt};
    color: {text};
    border: 1px solid {border};
    border-radius: 8px;
    padding: 6px 10px;
}}

QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
    border: 1px solid {accent};
}}

QComboBox QAbstractItemView {{
    background-color: {menu_bg};
    color: {text};
    border: 1px solid {border};
    selection-background-color: {accent_soft};
    selection-color: {text};
}}

QMenu {{
    background-color: {menu_bg};
    color: {text};
    border: 1px solid {border};
    border-radius: 8px;
    padding: 4px;
}}

QMenu::item {{
    padding: 8px 24px;
    border-radius: 4px;
}}

QMenu::item:selected {{
    background-color: {accent_soft};
    color: {text};
}}

QMenu::separator {{
    height: 1px;
    background: {border};
    margin: 4px 10px;
}}

QCheckBox, QRadioButton {{
    color: {text};
    spacing: 8px;
}}

QCheckBox::indicator, QRadioButton::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {border};
    border-radius: 4px;
    background: {bg_alt};
}}

QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
    background: {accent};
    border: 1px solid {accent};
}}

QSlider::groove:horizontal {{
    height: 4px;
    background: {border};
    border-radius: 2px;
}}

QSlider::handle:horizontal {{
    background: {accent};
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}}

QSlider::sub-page:horizontal {{
    background: {accent};
    border-radius: 2px;
}}

QScrollArea {{
    border: none;
    background: transparent;
}}

QScrollArea > QWidget > QWidget {{
    background: transparent;
}}

QScrollBar:vertical {{
    border: none;
    background: transparent;
    width: 10px;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background: {scrollbar};
    min-height: 30px;
    border-radius: 5px;
}}

QScrollBar::handle:vertical:hover {{
    background: {accent};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
}}

QScrollBar:horizontal {{
    border: none;
    background: transparent;
    height: 10px;
    margin: 0px;
}}

QScrollBar::handle:horizontal {{
    background: {scrollbar};
    min-width: 30px;
    border-radius: 5px;
}}

QScrollBar::handle:horizontal:hover {{
    background: {accent};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    height: 0px;
}}

QToolTip {{
    background-color: {surface_2};
    color: {text};
    border: 1px solid {border};
    padding: 6px 10px;
    border-radius: 6px;
}}

QTableWidget {{
    background-color: {surface};
    alternate-background-color: {bg_alt};
    color: {text};
    border: 1px solid {border};
    border-radius: 8px;
    gridline-color: {border_soft};
}}

QHeaderView::section {{
    background-color: {surface_2};
    color: {text_dim};
    border: none;
    padding: 8px;
    font-weight: 700;
}}

QTabWidget::pane {{
    border: 1px solid {border};
    border-radius: 8px;
    background: {surface};
}}

QTabBar::tab {{
    background: transparent;
    color: {text_dim};
    padding: 8px 16px;
    border: none;
    border-bottom: 2px solid transparent;
}}

QTabBar::tab:selected {{
    color: {text};
    border-bottom: 2px solid {accent};
}}

QTabBar::tab:hover {{
    color: {text};
}}
"""


def apply(app: QApplication, light: bool, accent_hex: str) -> None:
    palette = _palette(light, accent_hex)
    app.setStyleSheet(_QSS.format(**palette))