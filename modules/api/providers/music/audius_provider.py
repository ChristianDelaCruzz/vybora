import os, requests
from dotenv import load_dotenv
load_dotenv()
AUDIUS_API_KEY = os.getenv("AUDIUS_API_KEY")
BASE_URL = "https://api.audius.co/v1"

class AudiusError(Exception): pass

def _get(endpoint: str, params: dict | None = None) -> dict:
    headers = {}
    if AUDIUS_API_KEY:
        headers["Authorization"] = f"Bearer {AUDIUS_API_KEY}"
    try:
        r = requests.get(f"{BASE_URL}{endpoint}", headers=headers, params=params, timeout=10)
        if not r.ok: raise AudiusError(f"Error {r.status_code}")
        return r.json()
    except requests.RequestException as e:
        raise AudiusError(str(e))

def search_tracks(query: str, limit: int = 10) -> list[dict]:
    data = _get("/tracks/search", {"query": query, "limit": limit})
    return data.get("data", [])

def get_trending_tracks(limit: int = 10) -> list[dict]:
    data = _get("/tracks/trending", {"limit": limit})
    return data.get("data", [])