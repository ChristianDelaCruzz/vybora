"""Central configuration. Reads .env once and exposes project constants."""
from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# ==========================================
# TMDB (Movies & TV)
# ==========================================
TMDB_READ_TOKEN: str = os.getenv("TMDB_READ_TOKEN", "").strip()
TMDB_IMAGE_BASE: str = os.getenv("TMDB_IMAGE_BASE", "https://image.tmdb.org/t/p").rstrip("/")
TMDB_API_ROOT: str = "https://api.themoviedb.org/3"

# ==========================================
# Jamendo (Music)
# ==========================================
JAMENDO_CLIENT_ID: str = os.getenv("JAMENDO_CLIENT_ID", "e208ebdf").strip()
JAMENDO_API_ROOT: str = "https://api.jamendo.com/v3.0"

# ==========================================
# RAWG (Games)
# ==========================================
RAWG_API_KEY: str = os.getenv("RAWG_API_KEY", "").strip()
RAWG_API_ROOT: str = "https://api.rawg.io/api"

# ==========================================
# Paths
# ==========================================
DATA_DIR: Path = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)
DATABASE_PATH: Path = DATA_DIR / "vybora.db"

ASSETS_DIR: Path = PROJECT_ROOT / "assets"
PLACEHOLDER_POSTER: Path = ASSETS_DIR / "images" / "placeholder_poster.png"

# ==========================================
# VyBora palette (Dark Mode defaults)
# ==========================================
COLOR_BG = "#100E1B"
COLOR_SURFACE = "#1B1929"
COLOR_SURFACE_2 = "#29263B"
COLOR_PURPLE = "#7655EF"
COLOR_BLUE = "#3985FF"
COLOR_PINK = "#D946EF"
COLOR_TEXT = "#F5F3FF"
COLOR_TEXT_DIM = "#A5A0B8"

# ==========================================
# Helper functions
# ==========================================
def has_tmdb_token() -> bool:
    return bool(TMDB_READ_TOKEN)

def has_jamendo_id() -> bool:
    return bool(JAMENDO_CLIENT_ID)

def has_rawg_key() -> bool:
    return bool(RAWG_API_KEY)