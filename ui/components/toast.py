"""A single toast notification card + convenience helper."""
from PySide6.QtCore import Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QVBoxLayout, QGraphicsOpacityEffect, QWidget
)

from ui.components import icon_manager as icons
from ui.components.widgets import IconButton, Spinner
from ui.app_state import theme_state

KINDS = {
    "success": ("system/check-circle", "#10B981"),
    "error":   ("system/alert-circle", "#EF4444"),
    "warning": ("system/alert-triangle", "#F59E0B"),
    "info":    ("system/info", theme_state.accent_hex),
    "loading": ("system/loader-circle", theme_state.accent_hex),
}
TOAST_WIDTH = 340


class ToastWidget(QFrame):
    dismissed = Signal(object)

    def __init__(self, kind: str, title: str, message: str, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("glass")
        self.setFixedWidth(TOAST_WIDTH)
        self.kind = kind
        self.timer = None
        self.displayed = False
        self._duration = None

        row = QHBoxLayout(self)
        row.setContentsMargins(16, 12, 10, 12)
        row.setSpacing(12)

        self._icon = QLabel()
        self._icon.setFixedSize(26, 26)
        self._icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._spinner = Spinner(26, theme_state.accent_hex)

        row.addWidget(self._icon, alignment=Qt.AlignmentFlag.AlignTop)
        row.addWidget(self._spinner, alignment=Qt.AlignmentFlag.AlignTop)

        col = QVBoxLayout()
        col.setSpacing(2)

        self._title = QLabel()
        self._title.setWordWrap(True)

        self._message = QLabel()
        self._message.setWordWrap(True)

        col.addWidget(self._title)
        col.addWidget(self._message)
        row.addLayout(col, 1)

        close = IconButton("system/x", "Dismiss notification", 15)
        close.clicked.connect(lambda: self.dismissed.emit(self))
        row.addWidget(close, alignment=Qt.AlignmentFlag.AlignTop)

        self.set_content(kind, title, message)

    def set_content(self, kind: str, title: str, message: str) -> None:
        self.kind = kind
        icon_name, color = KINDS.get(kind, KINDS["info"])

        self._spinner.setVisible(kind == "loading")
        self._icon.setVisible(kind != "loading")

        if kind != "loading":
            try:
                self._icon.setPixmap(icons.pixmap(icon_name, 24, color))
            except Exception:
                self._icon.clear()

        self._title.setText(title)
        self._message.setText(message)
        self._message.setVisible(bool(message))
        self.setAccessibleName(f"{kind} notification: {title}")
        
        self.refresh_theme()
        self.adjustSize()

    def refresh_theme(self) -> None:
        icon_name, color = KINDS.get(self.kind, KINDS["info"])
        self.setStyleSheet(
            f"QFrame#glass {{ background-color: {theme_state.surface()};"
            f" border: 1px solid {theme_state.border()};"
            f" border-left: 3px solid {color}; border-radius: 12px; }}"
        )
        self._title.setStyleSheet(f"color: {theme_state.text()}; font-weight: 700; background: transparent;")
        self._message.setStyleSheet(f"color: {theme_state.text_dim()}; font-size: 13px; background: transparent;")


class Toast:
    """Convenience helper: Toast(window, title, message, kind).show_toast()."""

    def __init__(self, parent: QWidget, title: str, message: str = "",
                 kind: str = "info", duration_ms: int = 4200) -> None:
        self._parent = parent
        self._title = title
        self._message = message
        self._kind = kind
        self._duration = duration_ms
        self._widget: ToastWidget | None = None

    def show_toast(self) -> "Toast":
        if self._parent is None:
            return self

        toast = ToastWidget(self._kind, self._title, self._message, self._parent)
        toast.adjustSize()

        parent_rect = self._parent.rect()
        margin = 18
        x = max(margin, parent_rect.width() - toast.width() - margin)

        stack_y = 74
        for child in self._parent.findChildren(ToastWidget):
            if child.isVisible():
                stack_y += child.height() + 10

        toast.move(x, stack_y)
        toast.show()
        toast.raise_()

        effect = QGraphicsOpacityEffect(toast)
        toast.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity", toast)
        anim.setDuration(220)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.finished.connect(lambda t=toast: t.setGraphicsEffect(None))
        anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

        if self._duration:
            QTimer.singleShot(self._duration, lambda t=toast: self._dismiss(t))

        toast.dismissed.connect(self._dismiss)
        self._widget = toast
        return self

    def _dismiss(self, toast: ToastWidget) -> None:
        if toast is None or not toast.isVisible():
            return
        effect = toast.graphicsEffect() or QGraphicsOpacityEffect(toast)
        toast.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity", toast)
        anim.setDuration(180)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.finished.connect(toast.deleteLater)
        anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)