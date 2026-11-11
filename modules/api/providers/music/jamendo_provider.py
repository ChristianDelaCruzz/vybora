import os, requests
from dotenv import load_dotenv
load_dotenv()
JAMENDO_CLIENT_ID = os.getenv("JAMENDO_CLIENT_ID")
BASE_URL = "https://api.jamendo.com/v3.0"

class JamendoError(Exception): pass

def _get(endpoint: str, params: dict) -> dict:
    if not JAMENDO_CLIENT_ID: raise JamendoError("Missing Jamendo ID")
    params["client_id"] = JAMENDO_CLIENT_ID
    params["format"] = "json"
    try:
        r = requests.get(f"{BASE_URL}{endpoint}", params=params, timeout=10)
        if not r.ok: raise JamendoError(f"Error {r.status_code}")
        return r.json()
    except requests.RequestException as e:
        raise JamendoError(str(e))

def search_tracks(query: str, limit: int = 10) -> list[dict]:
    data = _get("/tracks/", {"search": query, "limit": limit, "audioformat": "mp32"})
    return [{"id": t["id"], "title": t["name"], "artist": t["artist_name"], "stream_url": t.get("audio"), "artwork": t.get("image")} for t in data.get("results", [])]

def get_popular_tracks(limit: int = 10) -> list[dict]:
    data = _get("/tracks/", {"order": "popularity_total", "limit": limit, "audioformat": "mp32"})
    return [{"id": t["id"], "title": t["name"], "artist": t["artist_name"], "stream_url": t.get("audio"), "artwork": t.get("image")} for t in data.get("results", [])]