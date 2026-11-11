"""Application-wide toast notifications."""

from typing import Optional

from PySide6.QtCore import QEasingCurve, QEvent, QObject, QPoint, QPropertyAnimation, QTimer
from PySide6.QtWidgets import QGraphicsOpacityEffect, QWidget

from ui.components.toast import ToastWidget
from ui.app_state import app_state # Import state

MARGIN, GAP, TOP_OFFSET = 18, 10, 74
DEFAULT_MS = 4200


class ToastHandle:
    def __init__(self, manager: "ToastManager", widget: ToastWidget) -> None:
        self._m, self._w = manager, widget

    def update(self, kind: str, title: str, message: str = "", duration_ms: Optional[int] = DEFAULT_MS) -> None:
        self._m._update(self._w, kind, title, message, duration_ms)

    def success(self, title: str, message: str = "") -> None:
        self.update("success", title, message)

    def error(self, title: str, message: str = "") -> None:
        self.update("error", title, message, 6000)

    def dismiss(self) -> None:
        self._m._dismiss(self._w)


class ToastManager(QObject):
    def __init__(self, host: QWidget, max_visible: int = 4) -> None:
        super().__init__(host)
        self.host = host
        self.max_visible = max_visible
        self._toasts: list[ToastWidget] = []
        self._anims: list = []
        host.installEventFilter(self)

    def _can_show(self) -> bool:
        return app_state.notifications_enabled and app_state.toast_notifications

    def show_success(self, title: str, message: str = "", duration_ms: int = DEFAULT_MS) -> ToastHandle | None:
        if not self._can_show(): return None
        return self._add("success", title, message, duration_ms)

    def show_error(self, title: str, message: str = "", duration_ms: int = 6000) -> ToastHandle | None:
        if not self._can_show(): return None
        return self._add("error", title, message, duration_ms)

    def show_warning(self, title: str, message: str = "", duration_ms: int = 5200) -> ToastHandle | None:
        if not self._can_show(): return None
        return self._add("warning", title, message, duration_ms)

    def show_info(self, title: str, message: str = "", duration_ms: int = DEFAULT_MS) -> ToastHandle | None:
        if not self._can_show(): return None
        return self._add("info", title, message, duration_ms)

    def show_loading(self, title: str, message: str = "") -> ToastHandle | None:
        if not self._can_show(): return None
        return self._add("loading", title, message, None)

    def clear(self) -> None:
        for t in list(self._toasts):
            self._remove(t)

    @property
    def toasts(self) -> list[ToastWidget]:
        return list(self._toasts)

    def visible_count(self) -> int:
        return sum(1 for t in self._toasts if t.displayed)

    def _add(self, kind: str, title: str, message: str, duration: Optional[int]) -> ToastHandle:
        toast = ToastWidget(kind, title, message, self.host)
        toast.hide()
        toast._duration = duration
        toast.dismissed.connect(self._dismiss)
        self._toasts.append(toast)
        self._relayout()
        return ToastHandle(self, toast)

    def _update(self, toast: ToastWidget, kind, title, message, duration) -> None:
        if toast not in self._toasts:
            return
        toast.set_content(kind, title, message)
        toast._duration = duration
        if toast.timer:
            toast.timer.stop()
        if toast.displayed:
            self._arm(toast)
        self._relayout()

    def _arm(self, toast: ToastWidget) -> None:
        if toast._duration:
            if toast.timer is None:
                toast.timer = QTimer(toast)
                toast.timer.setSingleShot(True)
                toast.timer.timeout.connect(lambda t=toast: self._dismiss(t))
            toast.timer.start(toast._duration)

    def _dismiss(self, toast: ToastWidget) -> None:
        if toast not in self._toasts:
            return
        if not toast.displayed:
            self._remove(toast)
            return
        effect = toast.graphicsEffect() or QGraphicsOpacityEffect(toast)
        toast.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity", toast)
        anim.setDuration(180)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.finished.connect(lambda t=toast: self._remove(t))
        anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def _remove(self, toast: ToastWidget) -> None:
        if toast in self._toasts:
            self._toasts.remove(toast)
            if toast.timer:
                toast.timer.stop()
            toast.hide()
            toast.deleteLater()
            self._relayout()

    def _relayout(self) -> None:
        y = TOP_OFFSET
        for i, toast in enumerate(self._toasts):
            if i >= self.max_visible:
                toast.hide()
                continue
            toast.adjustSize()
            target = QPoint(self.host.width() - toast.width() - MARGIN, y)
            if not toast.displayed:
                toast.displayed = True
                toast.move(self.host.width() + 10, y)
                toast.show()
                toast.raise_()
                self._fade_in(toast)
                self._arm(toast)
            self._slide(toast, target)
            y += toast.height() + GAP

    def _slide(self, toast: ToastWidget, target: QPoint) -> None:
        anim = QPropertyAnimation(toast, b"pos", toast)
        anim.setDuration(240)
        anim.setEndValue(target)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def _fade_in(self, toast: ToastWidget) -> None:
        effect = QGraphicsOpacityEffect(toast)
        toast.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity", toast)
        anim.setDuration(240)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.finished.connect(lambda t=toast: t.setGraphicsEffect(None))
        anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def eventFilter(self, obj, event) -> bool:
        if obj is self.host and event.type() == QEvent.Type.Resize:
            for t in self._toasts:
                if t.displayed:
                    t.move(self.host.width() - t.width() - MARGIN, t.y())
            QTimer.singleShot(0, self._relayout)
        return False