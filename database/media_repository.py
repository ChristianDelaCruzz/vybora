
"""Persistence for TMDB items and per-user favorites.

TEMP_USER_ID is a placeholder until the authentication module lands.
"""
from __future__ import annotations

from typing import Iterable

from database.connection import get_connection, transaction

TEMP_USER_ID = 1


def upsert_media_item(item: dict, media_type: str) -> None:
    if media_type not in ("movie", "tv"):
        raise ValueError("media_type must be 'movie' or 'tv'")
    title = item.get("title") or item.get("name") or "Untitled"
    release = item.get("release_date") or item.get("first_air_date") or ""
    with transaction() as conn:
        conn.execute(
            """
            INSERT INTO tmdb_media_cache
                (tmdb_id, media_type, title, overview, poster_path,
                 backdrop_path, release_date, vote_average)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(tmdb_id, media_type) DO UPDATE SET
                title=excluded.title,
                overview=excluded.overview,
                poster_path=excluded.poster_path,
                backdrop_path=excluded.backdrop_path,
                release_date=excluded.release_date,
                vote_average=excluded.vote_average,
                cached_at=CURRENT_TIMESTAMP
            """,
            (
                int(item["id"]),
                media_type,
                title,
                item.get("overview"),
                item.get("poster_path"),
                item.get("backdrop_path"),
                release,
                item.get("vote_average"),
            ),
        )


def upsert_many(items: Iterable[dict], media_type: str) -> None:
    for it in items:
        upsert_media_item(it, media_type)


def is_favorite(tmdb_id: int, media_type: str) -> bool:
    row = get_connection().execute(
        "SELECT 1 FROM media_favorites WHERE user_id=? AND tmdb_id=? AND media_type=?",
        (TEMP_USER_ID, tmdb_id, media_type),
    ).fetchone()
    return row is not None


def toggle_favorite(tmdb_id: int, media_type: str) -> bool:
    """Return the new state after toggling."""
    if is_favorite(tmdb_id, media_type):
        with transaction() as conn:
            conn.execute(
                "DELETE FROM media_favorites WHERE user_id=? AND tmdb_id=? AND media_type=?",
                (TEMP_USER_ID, tmdb_id, media_type),
            )
        return False
    with transaction() as conn:
        conn.execute(
            "INSERT INTO media_favorites (user_id, tmdb_id, media_type) VALUES (?,?,?)",
            (TEMP_USER_ID, tmdb_id, media_type),
        )
    return True