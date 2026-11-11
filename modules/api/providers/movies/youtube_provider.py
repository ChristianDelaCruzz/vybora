"""YouTube Data API v3 for official trailers."""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
BASE_URL = "https://www.googleapis.com/youtube/v3"


class YouTubeError(Exception):
    pass


def _get(endpoint: str, params: dict) -> dict:
    if not YOUTUBE_API_KEY:
        raise YouTubeError("YOUTUBE_API_KEY is missing from .env")
    params["key"] = YOUTUBE_API_KEY
    try:
        r = requests.get(f"{BASE_URL}{endpoint}", params=params, timeout=10)
        if not r.ok:
            raise YouTubeError(f"YouTube error {r.status_code}: {r.text[:200]}")
        return r.json()
    except requests.RequestException as e:
        raise YouTubeError(f"Network error: {e}")


def search_trailers(query: str, max_results: int = 5) -> list[dict]:
    """Search for official trailers."""
    data = _get("/search", {
        "part": "snippet",
        "q": f"{query} official trailer",
        "type": "video",
        "maxResults": max_results,
        "videoEmbeddable": "true",
    })
    results = []
    for item in data.get("items", []):
        results.append({
            "video_id": item["id"]["videoId"],
            "title": item["snippet"]["title"],
            "channel": item["snippet"]["channelTitle"],
            "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
            "description": item["snippet"]["description"],
        })
    return results


def get_video_details(video_id: str) -> dict | None:
    """Get details for a specific video, including embeddable status."""
    data = _get("/videos", {
        "part": "snippet,contentDetails,status",
        "id": video_id,
    })
    items = data.get("items", [])
    if not items:
        return None
    item = items[0]
    return {
        "video_id": video_id,
        "title": item["snippet"]["title"],
        "channel": item["snippet"]["channelTitle"],
        "embeddable": item["status"].get("embeddable", False),
        "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
    }