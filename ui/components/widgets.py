"""Reusable VyBora widgets."""
from __future__ import annotations

from PySide6.QtCore import Qt, QSize, QVariantAnimation, QEasingCurve, QTimer
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPen
from PySide6.QtWidgets import (
    QPushButton, QSizePolicy, QWidget, QGridLayout, QLabel,
    QVBoxLayout, QHBoxLayout, QFrame,
)

from config.settings import COLOR_PURPLE, COLOR_BLUE, COLOR_PINK, COLOR_TEXT, COLOR_TEXT_DIM
from ui.components.icon_manager import get_icon


# ---------------------------------------------------------------------------
# GradientButton
# ---------------------------------------------------------------------------
class GradientButton(QPushButton):
    """Primary action button with animated hover glow."""

    def __init__(self, text: str = "", icon_name: str = "", parent=None, height: int = 50) -> None:
        super().__init__(text, parent)
        self._glow = 0.0
        self._pressed = False
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(height)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self._anim = QVariantAnimation(self, startValue=0.0, endValue=1.0, duration=180)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.valueChanged.connect(self._on_glow)

        if icon_name:
            self.setIcon(get_icon(icon_name, "#FFFFFF", 18))
            self.setIconSize(QSize(18, 18))

    def _on_glow(self, v) -> None:
        self._glow = float(v)
        self.update()

    def enterEvent(self, e) -> None:
        self._anim.setDirection(QVariantAnimation.Direction.Forward)
        self._anim.start()
        super().enterEvent(e)

    def leaveEvent(self, e) -> None:
        self._anim.setDirection(QVariantAnimation.Direction.Backward)
        self._anim.start()
        super().leaveEvent(e)

    def mousePressEvent(self, e) -> None:
        self._pressed = True
        self.update()
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e) -> None:
        self._pressed = False
        self.update()
        super().mouseReleaseEvent(e)

    def paintEvent(self, _e) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = self.rect().adjusted(1, 1, -1, -1)
        if self._pressed:
            r = r.adjusted(1, 1, -1, -1)

        grad = QLinearGradient(r.topLeft(), r.topRight())
        c1, c2 = QColor(COLOR_PURPLE), QColor(COLOR_BLUE)
        pink = QColor(COLOR_PINK)

        mix = lambda a, b, t: QColor(
            int(a.red() + (b.red() - a.red()) * t),
            int(a.green() + (b.green() - a.green()) * t),
            int(a.blue() + (b.blue() - a.blue()) * t),
        )
        grad.setColorAt(0, mix(c1, pink, self._glow * 0.55))
        grad.setColorAt(1, mix(c2, c1, self._glow * 0.5))

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(grad)
        p.drawRoundedRect(r, 8, 8)

        if self.hasFocus():
            p.setPen(QPen(QColor("#FFFFFF"), 1.5))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRoundedRect(r.adjusted(1, 1, -1, -1), 7, 7)

        p.setPen(QColor("#FFFFFF"))
        font = self.font()
        font.setBold(True)
        p.setFont(font)
        fm = self.fontMetrics()

        icon_w = 26 if not self.icon().isNull() else 0
        total = icon_w + fm.horizontalAdvance(self.text())
        x = r.center().x() - total / 2

        if icon_w:
            p.drawPixmap(int(x), int(r.center().y() - 9), self.icon().pixmap(18, 18))

        p.drawText(
            r.adjusted(int(x + icon_w), 0, 0, 0),
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            self.text(),
        )


# ---------------------------------------------------------------------------
# IconButton
# ---------------------------------------------------------------------------
class IconButton(QPushButton):
    """Square, borderless icon button with hover/pressed feedback."""

    def __init__(self, icon_name: str, tooltip: str = "", size: int = 20,
                 color: str = "#FFFFFF", parent=None, button_size: int | None = None) -> None:
        super().__init__(parent)
        self._icon_name = icon_name
        self._icon_size = size
        self._color = color
        btn = button_size or (size + 16)
        self.setFixedSize(btn, btn)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(tooltip)
        self.setAccessibleName(tooltip or icon_name)
        self.setStyleSheet(self._style(hover=False, pressed=False))
        self._refresh_icon()

    def _style(self, hover: bool, pressed: bool) -> str:
        if pressed:
            bg = "rgba(255,255,255,30)"
        elif hover:
            bg = "rgba(255,255,255,18)"
        else:
            bg = "transparent"
        radius = self.width() // 2
        return (
            f"QPushButton {{ background-color: {bg}; border: none;"
            f"border-radius: {radius}px; }}"
        )

    def _refresh_icon(self) -> None:
        self.setIcon(get_icon(self._icon_name, self._color, self._icon_size))
        self.setIconSize(QSize(self._icon_size, self._icon_size))

    def set_icon_name(self, icon_name: str, color: str | None = None) -> None:
        """Update the icon, and optionally the color. Re-renders immediately."""
        self._icon_name = icon_name
        if color is not None:
            self._color = color
        self._refresh_icon()

    def enterEvent(self, e) -> None:
        self.setStyleSheet(self._style(hover=True, pressed=False))
        super().enterEvent(e)

    def leaveEvent(self, e) -> None:
        self.setStyleSheet(self._style(hover=False, pressed=False))
        super().leaveEvent(e)

    def mousePressEvent(self, e) -> None:
        self.setStyleSheet(self._style(hover=True, pressed=True))
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e) -> None:
        self.setStyleSheet(self._style(hover=True, pressed=False))
        super().mouseReleaseEvent(e)


# ---------------------------------------------------------------------------
# secondary_button
# ---------------------------------------------------------------------------
def secondary_button(text: str, icon_name: str = "", danger: bool = False,
                     parent=None, height: int = 42) -> QPushButton:
    """Flat, muted button used for secondary actions (Back, Cancel, etc.)."""
    btn = QPushButton(text, parent)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setMinimumHeight(height)
    if icon_name:
        btn.setIcon(get_icon(icon_name, COLOR_TEXT, 16))
        btn.setIconSize(QSize(16, 16))

    accent = "#EF4444" if danger else COLOR_BLUE
    btn.setStyleSheet(
        f"QPushButton {{"
        f"  background-color: rgba(255,255,255,8);"
        f"  color: {COLOR_TEXT};"
        f"  border: 1px solid rgba(255,255,255,20);"
        f"  border-radius: 8px;"
        f"  padding: 0 16px;"
        f"  font-weight: 600;"
        f"  font-size: 13px;"
        f"}}"
        f"QPushButton:hover {{"
        f"  border: 1px solid {accent};"
        f"  background-color: rgba(255,255,255,14);"
        f"}}"
        f"QPushButton:disabled {{ color: {COLOR_TEXT_DIM}; }}"
    )
    return btn


# ---------------------------------------------------------------------------
# section_header / page_title
# ---------------------------------------------------------------------------
def section_header(title: str, subtitle: str = "") -> QWidget:
    """Two-line section header: bold title, muted subtitle."""
    box = QWidget()
    lay = QVBoxLayout(box)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(2)

    t = QLabel(title)
    t.setStyleSheet(f"color: {COLOR_TEXT}; font-size: 18px; font-weight: 700;")
    lay.addWidget(t)

    if subtitle:
        s = QLabel(subtitle)
        s.setStyleSheet(f"color: {COLOR_TEXT_DIM}; font-size: 12px;")
        lay.addWidget(s)

    return box


def page_title(title: str, subtitle: str = "") -> QWidget:
    """Large page title with optional subtitle."""
    box = QWidget()
    lay = QVBoxLayout(box)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(4)

    t = QLabel(title)
    t.setStyleSheet(f"color: {COLOR_TEXT}; font-size: 26px; font-weight: 800;")
    lay.addWidget(t)

    if subtitle:
        s = QLabel(subtitle)
        s.setStyleSheet(f"color: {COLOR_TEXT_DIM}; font-size: 13px;")
        lay.addWidget(s)

    return box


# ---------------------------------------------------------------------------
# clear_layout
# ---------------------------------------------------------------------------
def clear_layout(layout) -> None:
    """Recursively remove and delete everything inside a layout."""
    while layout.count():
        item = layout.takeAt(0)
        w = item.widget()
        if w is not None:
            w.setParent(None)
            w.deleteLater()
            continue
        sub = item.layout()
        if sub is not None:
            clear_layout(sub)
            sub.deleteLater()


# ---------------------------------------------------------------------------
# Spinner
# ---------------------------------------------------------------------------
class Spinner(QWidget):
    """Simple rotating arc spinner."""

    def __init__(self, diameter: int = 24, color: str = COLOR_PURPLE, parent=None) -> None:
        super().__init__(parent)
        self._diameter = diameter
        self._color = QColor(color)
        self._angle = 0
        self.setFixedSize(diameter, diameter)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(16)

    def _tick(self) -> None:
        self._angle = (self._angle + 8) % 360
        self.update()

    def paintEvent(self, _e) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = self.rect().adjusted(3, 3, -3, -3)
        pen = QPen(self._color, 3)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.drawArc(r, -self._angle * 16, 270 * 16)


# ---------------------------------------------------------------------------
# EmptyState
# ---------------------------------------------------------------------------
class EmptyState(QWidget):
    """Icon + title + message + optional action button."""

    def __init__(self, icon_name: str, title: str, message: str = "",
                 action_label: str = "", action_callback=None, parent=None) -> None:
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 40, 24, 40)
        lay.setSpacing(10)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon = QLabel()
        icon.setPixmap(get_icon(icon_name, COLOR_TEXT_DIM, 48))
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(icon)

        t = QLabel(title)
        t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t.setStyleSheet(f"color: {COLOR_TEXT}; font-size: 16px; font-weight: 700;")
        lay.addWidget(t)

        if message:
            m = QLabel(message)
            m.setAlignment(Qt.AlignmentFlag.AlignCenter)
            m.setWordWrap(True)
            m.setStyleSheet(f"color: {COLOR_TEXT_DIM}; font-size: 13px;")
            lay.addWidget(m)

        if action_label and action_callback:
            btn = GradientButton(action_label, height=40)
            btn.setFixedWidth(220)
            btn.clicked.connect(lambda _c=False: action_callback())
            lay.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)


# ---------------------------------------------------------------------------
# CardGrid
# ---------------------------------------------------------------------------
class CardGrid(QWidget):
    """Responsive grid that stretches cards to completely fill the row."""

    def __init__(self, min_card_width: int = 220, spacing: int = 16, parent=None) -> None:
        super().__init__(parent)
        self._min = min_card_width
        self._spacing = spacing
        self._widgets: list[QWidget] = []
        self._cols = 0
        self._grid = QGridLayout(self)
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setSpacing(spacing)
        self._grid.setAlignment(Qt.AlignmentFlag.AlignTop)

    def set_widgets(self, widgets: list[QWidget]) -> None:
        self.clear()
        self._widgets = list(widgets)
        self._cols = 0
        self._relayout()

    def clear(self) -> None:
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
                item.widget().deleteLater()
        self._widgets = []

    def _columns(self) -> int:
        return max(1, (self.width() + self._spacing) // (self._min + self._spacing))

    def _relayout(self) -> None:
        cols = self._columns()
        if cols == self._cols and self._grid.count() == len(self._widgets):
            return
        self._cols = cols

        while self._grid.count():
            self._grid.takeAt(0)

        for c in range(max(cols, 12)):
            if c < cols:
                self._grid.setColumnStretch(c, 1)
            else:
                self._grid.setColumnStretch(c, 0)

        for i, w in enumerate(self._widgets):
            self._grid.addWidget(w, i // cols, i % cols, Qt.AlignmentFlag.AlignTop)
            w.show()

    def resizeEvent(self, e) -> None:
        super().resizeEvent(e)
        self._relayout()