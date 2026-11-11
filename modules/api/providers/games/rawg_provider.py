"""RAWG Provider - Game metadata (no playable files)."""
import requests
from config.settings import RAWG_API_KEY
from modules.api.core.exceptions import ProviderUnavailable

class RAWGProvider:
    NAME = "RAWG"
    CATEGORY = "games"
    BASE_URL = "https://api.rawg.io/api"

    def __init__(self):
        self.api_key = RAWG_API_KEY
        if not self.api_key:
            raise ProviderUnavailable(self.NAME)

    def _request(self, endpoint: str, params: dict = None) -> dict:
        params = params or {}
        params["key"] = self.api_key
        try:
            r = requests.get(f"{self.BASE_URL}{endpoint}", params=params, timeout=10)
            r.raise_for_status()
            return r.json()
        except requests.RequestException:
            raise ProviderUnavailable(self.NAME)

    def search_games(self, query: str, page: int = 1) -> dict:
        data = self._request("/games", {"search": query, "page": page, "page_size": 20})
        results = []
        for game in data.get("results", []):
            results.append({
                "provider": self.NAME,
                "external_id": str(game["id"]),
                "category": "game",
                "title": game.get("name"),
                "description": "",  # RAWG list endpoint doesn't include full description
                "artwork_url": game.get("background_image"),
                "release_date": game.get("released"),
                "rating": game.get("rating"),
                "playable": False,  # RAWG does NOT provide playable files
                "playback_url": None,
                "playback_type": None,
                "raw_metadata": game,
            })
        return {
            "success": True, "provider": self.NAME, "category": "games",
            "data": results,
            "pagination": {"page": page, "total_pages": None, "total_results": data.get("count", 0)},
            "error": None,
        }

    def get_game_details(self, external_id: str) -> dict:
        data = self._request(f"/games/{external_id}")
        return {
            "success": True, "provider": self.NAME, "category": "games",
            "data": {
                "provider": self.NAME,
                "external_id": str(data["id"]),
                "category": "game",
                "title": data.get("name"),
                "description": data.get("description_raw", ""),
                "artwork_url": data.get("background_image"),
                "release_date": data.get("released"),
                "rating": data.get("rating"),
                "playable": False,  # Metadata only
                "raw_metadata": data,
            },
            "pagination": None, "error": None,
        }