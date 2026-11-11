"""Run slow work (network, big queries) off the GUI thread."""
import logging
from typing import Any, Callable, Optional
from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal

log = logging.getLogger(__name__)

class _Signals(QObject):
    done = Signal(object)
    failed = Signal(object)

class _Task(QRunnable):
    def __init__(self, fn: Callable, args: tuple, kwargs: dict) -> None:
        super().__init__()
        self.fn, self.args, self.kwargs = fn, args, kwargs
        self.signals = _Signals()
        self.setAutoDelete(True)

    def run(self) -> None:
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception as exc:
            try:
                self.signals.failed.emit(exc)
            except RuntimeError:
                pass
            return
        
        try:
            self.signals.done.emit(result)
        except RuntimeError:
            pass

def run_async(fn: Callable, *args: Any, on_done: Optional[Callable[[Any], None]] = None,
              on_error: Optional[Callable[[Exception], None]] = None, **kwargs: Any) -> None:
    task = _Task(fn, args, kwargs)

    def _finish(callback, value):
        if callback:
            try:
                callback(value)
            except RuntimeError:
                pass # The widget was deleted while the task was running

    task.signals.done.connect(lambda v: _finish(on_done, v))
    task.signals.failed.connect(lambda e: _finish(on_error, e))
    QThreadPool.globalInstance().start(task)