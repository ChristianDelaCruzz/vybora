"""Reusable animation helpers for PySide6."""
from PySide6.QtCore import (
    QPropertyAnimation, QEasingCurve, QPoint,
    QParallelAnimationGroup
)
from PySide6.QtWidgets import QGraphicsOpacityEffect, QWidget
from modules.settings.settings_manager import settings_manager

def fade_in(widget: QWidget, duration: int = 400) -> None:
    s = settings_manager.current_settings
    if s and not s.get("animations", 1):
        widget.show()
        return
        
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)

    anim = QPropertyAnimation(effect, b"opacity", widget)
    anim.setDuration(duration)
    anim.setStartValue(0.0)
    anim.setEndValue(1.0)
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def on_finished():
        widget.setGraphicsEffect(None)

    anim.finished.connect(on_finished)
    widget._fade_anim = anim
    anim.start()

def slide_up_and_fade(widget: QWidget, duration: int = 500, offset: int = 30) -> None:
    s = settings_manager.current_settings
    if s and not s.get("animations", 1):
        widget.show()
        return

    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)

    fade = QPropertyAnimation(effect, b"opacity", widget)
    fade.setDuration(duration)
    fade.setStartValue(0.0)
    fade.setEndValue(1.0)
    fade.setEasingCurve(QEasingCurve.Type.OutCubic)

    end_pos = widget.pos()
    start_pos = end_pos + QPoint(0, offset)

    slide = QPropertyAnimation(widget, b"pos", widget)
    slide.setDuration(duration)
    slide.setStartValue(start_pos)
    slide.setEndValue(end_pos)
    slide.setEasingCurve(QEasingCurve.Type.OutCubic)

    group = QParallelAnimationGroup(widget)
    group.addAnimation(fade)
    group.addAnimation(slide)

    def on_finished():
        widget.move(end_pos)
        widget.setGraphicsEffect(None)

    group.finished.connect(on_finished)
    widget._anim_group = group
    group.start()

def add_hover_animation(button, normal_style: str, hover_style: str, duration: int = 0) -> None:
    button._normal_style = normal_style
    button._hover_style = hover_style
    button.setStyleSheet(normal_style)

    def _enter(event):
        button.setStyleSheet(button._hover_style)
        button.enterEvent(event)

    def _leave(event):
        button.setStyleSheet(button._normal_style)
        button.leaveEvent(event)

    button.enterEvent = _enter
    button.leaveEvent = _leave