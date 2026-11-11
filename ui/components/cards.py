"""Reusable media cards wrappers."""
from ui.components.media_card import MediaCard

def game_card(g: dict, favorite: bool = False, show_favorite: bool = True, badge: str = "") -> MediaCard:
    # Map game data to your MediaCard
    return MediaCard(g, "game")

def video_card(v: dict, favorite: bool = False, show_favorite: bool = True, badge: str = "") -> MediaCard:
    return MediaCard(v, "movie")

def music_card(m: dict, favorite: bool = False, show_favorite: bool = True, badge: str = "") -> MediaCard:
    return MediaCard(m, "movie")