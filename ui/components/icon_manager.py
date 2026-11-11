"""Utility for loading and colorizing SVG icons."""
import os
from pathlib import Path
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtSvg import QSvgRenderer

from config.settings import PROJECT_ROOT

ICON_DIR = PROJECT_ROOT / "assets" / "icons"

# Standard colors used by the app
WHITE = "#FFFFFF"
DEFAULT = "#A5A0B8"
ACCENT = "#D946EF"


def _render_svg(name: str, color: str, size: int) -> QPixmap:
    """Render an SVG by name into a transparent QPixmap at the given size/color."""
    file_path = ICON_DIR / f"{name}.svg"

    pix = QPixmap(size, size)
    pix.fill(QColor("transparent"))

    if not file_path.exists():
        return pix

    try:
        svg_data = file_path.read_text(encoding="utf-8")
        svg_data = svg_data.replace("currentColor", color)
        renderer = QSvgRenderer(svg_data.encode("utf-8"))
        if not renderer.isValid():
            return pix
        painter = QPainter(pix)
        renderer.render(painter)
        painter.end()
    except Exception:
        # Never let an icon problem crash the UI.
        pass

    return pix


def get_icon(name: str, color: str = DEFAULT, size: int = 24) -> QIcon:
    """Loads an SVG by name, colors it, and returns a QIcon."""
    return QIcon(_render_svg(name, color, size))


def pixmap(name: str, size: int = 24, color: str = WHITE) -> QPixmap:
    """Loads an SVG by name and returns a colorized QPixmap of the given size.

    Signature matches what toast.py and other widgets call:
        icons.pixmap(icon_name, 24, color)
    """
    return _render_svg(name, color, size)