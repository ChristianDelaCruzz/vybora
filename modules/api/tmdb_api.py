"""TMDB API integration for Movies & TV."""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

TMDB_READ_TOKEN = os.getenv("TMDB_READ_TOKEN")
BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE = "https://image.tmdb.org/t/p/"


class TMDBError(Exception):
    pass


def _headers() -> dict:
    if not TMDB_READ_TOKEN:
        raise TMDBError("TMDB_READ_TOKEN is missing from .env")
    return {
        "Authorization": f"Bearer {TMDB_READ_TOKEN}",
        "accept": "application/json",
    }


def _get(endpoint: str, params: dict | None = None) -> dict:
    url = f"{BASE_URL}{endpoint}"
    try:
        r = requests.get(url, headers=_headers(), params=params, timeout=10)
        if not r.ok:
            raise TMDBError(f"TMDB error {r.status_code}: {r.text[:200]}")
        return r.json()
    except requests.RequestException as e:
        raise TMDBError(f"Network error: {e}")


def search(media_type: str, query: str, page: int = 1) -> list[dict]:
    data = _get(f"/search/{media_type}", {"query": query, "page": page})
    return data.get("results", [])


def get_popular(media_type: str, page: int = 1) -> list[dict]:
    data = _get(f"/{media_type}/popular", {"page": page})
    return data.get("results", [])


def get_details(media_type: str, tmdb_id: int) -> dict:
    return _get(f"/{media_type}/{tmdb_id}", {"append_to_response": "videos,credits,similar,watch/providers"})


def image_url(path: str | None, size: str = "w342") -> str | None:
    if not path:
        return None
    return f"{IMAGE_BASE}{size}{path}"


def get_trailer_key(tmdb_id: int, media_type: str) -> str | None:
    data = get_details(media_type, tmdb_id)
    videos = data.get("videos", {}).get("results", [])
    for v in videos:
        if v.get("site") == "YouTube" and v.get("type") == "Trailer":
            return v.get("key")
    return None