"""Centralized theme state with Accent Color support."""
from config.settings import (
    COLOR_BG, COLOR_SURFACE, COLOR_TEXT, COLOR_TEXT_DIM, 
    COLOR_PURPLE, COLOR_BLUE, COLOR_PINK
)

class ThemeState:
    def __init__(self):
        self.is_light = False
        self.accent_hex = COLOR_PURPLE
        self.accent_rgba = "rgba(118, 85, 239, 0.15)"

    def set_accent(self, color_name: str):
        if color_name == "Electric Blue":
            self.accent_hex = COLOR_BLUE
            self.accent_rgba = "rgba(57, 133, 255, 0.15)"
        elif color_name == "Pink":
            self.accent_hex = COLOR_PINK
            self.accent_rgba = "rgba(217, 70, 239, 0.15)"
        else:
            self.accent_hex = COLOR_PURPLE
            self.accent_rgba = "rgba(118, 85, 239, 0.15)"

    def bg(self) -> str:
        return "#F5F3FF" if self.is_light else COLOR_BG

    def surface(self) -> str:
        return "#FFFFFF" if self.is_light else COLOR_SURFACE

    def text(self) -> str:
        return "#100E1B" if self.is_light else COLOR_TEXT

    def text_dim(self) -> str:
        return "#5B5675" if self.is_light else COLOR_TEXT_DIM

    def border(self) -> str:
        return "#D1CCE0" if self.is_light else "rgba(255, 255, 255, 20)"

    def icon_color(self) -> str:
        return "#100E1B" if self.is_light else "#A5A0B8"

theme_state = ThemeState()