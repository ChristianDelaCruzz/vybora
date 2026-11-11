"""TMDB Provider - Wraps existing TMDB logic into standardized API responses."""
import requests
from config.settings import has_tmdb_token
from modules.api.core.exceptions import ProviderUnavailable, InvalidResponse

class TMDBProvider:
    NAME = "TMDB"
    CATEGORY = "movies_tv"
    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

    def __init__(self):
        from config.settings import TMDB_READ_TOKEN
        self.token = TMDB_READ_TOKEN
        if not self.token:
            raise ProviderUnavailable(self.NAME)

    def _headers(self):
        return {"Authorization": f"Bearer {self.token}", "accept": "application/json"}

    def _request(self, endpoint: str, params: dict = None) -> dict:
        try:
            r = requests.get(
                f"{self.BASE_URL}{endpoint}",
                headers=self._headers(),
                params=params or {},
                timeout=10
            )
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            raise ProviderUnavailable(self.NAME)

    def get_popular(self, media_type: str = "movie", page: int = 1) -> dict:
        data = self._request(f"/{media_type}/popular", {"page": page})
        results = []
        for item in data.get("results", []):
            results.append({
                "provider": self.NAME,
                "external_id": str(item["id"]),
                "category": media_type,
                "title": item.get("title") or item.get("name"),
                "description": item.get("overview", ""),
                "artwork_url": f"{self.IMAGE_BASE}{item['poster_path']}" if item.get("poster_path") else None,
                "backdrop_url": f"{self.IMAGE_BASE}{item['backdrop_path']}" if item.get("backdrop_path") else None,
                "release_date": item.get("release_date") or item.get("first_air_date"),
                "rating": item.get("vote_average"),
                "raw_metadata": item,
            })
        return {
            "success": True,
            "provider": self.NAME,
            "category": "movies_tv",
            "data": results,
            "pagination": {
                "page": data.get("page", 1),
                "total_pages": data.get("total_pages", 1),
                "total_results": data.get("total_results", 0),
            },
            "error": None,
        }

    def search(self, query: str, media_type: str = "movie", page: int = 1) -> dict:
        data = self._request(f"/search/{media_type}", {"query": query, "page": page})
        results = []
        for item in data.get("results", []):
            results.append({
                "provider": self.NAME,
                "external_id": str(item["id"]),
                "category": media_type,
                "title": item.get("title") or item.get("name"),
                "description": item.get("overview", ""),
                "artwork_url": f"{self.IMAGE_BASE}{item['poster_path']}" if item.get("poster_path") else None,
                "release_date": item.get("release_date") or item.get("first_air_date"),
                "rating": item.get("vote_average"),
                "raw_metadata": item,
            })
        return {
            "success": True,
            "provider": self.NAME,
            "category": "movies_tv",
            "data": results,
            "pagination": {
                "page": data.get("page", 1),
                "total_pages": data.get("total_pages", 1),
                "total_results": data.get("total_results", 0),
            },
            "error": None,
        }

    def get_details(self, media_type: str, external_id: str) -> dict:
        data = self._request(f"/{media_type}/{external_id}", {"append_to_response": "videos,credits"})
        
        # Resolve trailer if available
        playback_url = None
        playback_type = None
        videos = data.get("videos", {}).get("results", [])
        for vid in videos:
            if vid.get("site") == "YouTube" and vid.get("type") in ("Trailer", "Teaser"):
                playback_url = f"https://www.youtube.com/embed/{vid['key']}"
                playback_type = "youtube"
                break

        item = {
            "provider": self.NAME,
            "external_id": str(data["id"]),
            "category": media_type,
            "title": data.get("title") or data.get("name"),
            "description": data.get("overview", ""),
            "artwork_url": f"{self.IMAGE_BASE}{data['poster_path']}" if data.get("poster_path") else None,
            "backdrop_url": f"{self.IMAGE_BASE}{data['backdrop_path']}" if data.get("backdrop_path") else None,
            "release_date": data.get("release_date") or data.get("first_air_date"),
            "rating": data.get("vote_average"),
            "playable": playback_url is not None,
            "playback_url": playback_url,
            "playback_type": playback_type,
            "raw_metadata": data,
        }
        return {"success": True, "provider": self.NAME, "category": "movies_tv", "data": item, "pagination": None, "error": None}