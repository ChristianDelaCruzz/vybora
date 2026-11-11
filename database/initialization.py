"""Idempotent schema creation + full VyBora media architecture."""
from __future__ import annotations
from database.connection import get_connection


_SCHEMA = """
-- ==========================================
-- CORE USERS & AUTH
-- ==========================================
CREATE TABLE IF NOT EXISTS users (
    user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT    NOT NULL UNIQUE,
    email         TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    salt          TEXT    NOT NULL,
    role          TEXT    NOT NULL CHECK(role IN ('Admin', 'User')),
    created_at    TEXT    DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- LEGACY TMDB CACHE (kept for backward compat)
-- ==========================================
CREATE TABLE IF NOT EXISTS tmdb_media_cache (
    tmdb_id       INTEGER NOT NULL,
    media_type    TEXT    NOT NULL CHECK(media_type IN ('movie','tv')),
    title         TEXT    NOT NULL,
    overview      TEXT,
    poster_path   TEXT,
    backdrop_path TEXT,
    release_date  TEXT,
    vote_average  REAL,
    cached_at     TEXT DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (tmdb_id, media_type)
);

CREATE TABLE IF NOT EXISTS media_favorites (
    user_id    INTEGER NOT NULL,
    tmdb_id    INTEGER NOT NULL,
    media_type TEXT    NOT NULL CHECK(media_type IN ('movie','tv')),
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, tmdb_id, media_type),
    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ==========================================
-- UNIFIED MEDIA ARCHITECTURE
-- (Movies, TV, Music, Games from any provider)
-- ==========================================
CREATE TABLE IF NOT EXISTS media_items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    provider        TEXT NOT NULL,          -- 'TMDB', 'Jamendo', 'RAWG', etc.
    external_id     TEXT NOT NULL,          -- ID from the provider
    category        TEXT NOT NULL,          -- 'movie', 'tv', 'music', 'game'
    title           TEXT NOT NULL,
    description     TEXT,
    artwork_url     TEXT,
    release_date    TEXT,
    rating          REAL,
    raw_metadata    TEXT,                   -- JSON string for detail views
    last_fetched_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(provider, external_id, category)
);

CREATE TABLE IF NOT EXISTS media_sources (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    media_item_id      INTEGER NOT NULL,
    source_type        TEXT NOT NULL,       -- 'local_exe', 'html5_url', 'audio_stream', 'video_stream', 'youtube'
    source_reference   TEXT NOT NULL,       -- path or URL
    added_by_user_id   INTEGER,
    is_verified        INTEGER DEFAULT 0,
    created_at         TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (media_item_id)    REFERENCES media_items(id) ON DELETE CASCADE,
    FOREIGN KEY (added_by_user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS user_favorites (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL,
    media_item_id INTEGER NOT NULL,
    created_at    TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, media_item_id),
    FOREIGN KEY (user_id)       REFERENCES users(user_id)       ON DELETE CASCADE,
    FOREIGN KEY (media_item_id) REFERENCES media_items(id)      ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS playback_history (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    media_item_id   INTEGER NOT NULL,
    last_position_ms INTEGER DEFAULT 0,
    last_played_at  TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)       REFERENCES users(user_id)       ON DELETE CASCADE,
    FOREIGN KEY (media_item_id) REFERENCES media_items(id)      ON DELETE CASCADE
);
"""


def initialize_database() -> None:
    conn = get_connection()
    
    # 1. Create the base tables
    with conn:
        conn.executescript(_SCHEMA)

    cursor = conn.cursor()

    # 2. Create user_settings with ON DELETE CASCADE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_settings (
            user_id INTEGER PRIMARY KEY,
            theme TEXT DEFAULT 'Dark Mode',
            accent_color TEXT DEFAULT 'Purple',
            font_size TEXT DEFAULT 'Medium',
            animations INTEGER DEFAULT 1,
            sidebar TEXT DEFAULT 'Expanded',
            autoplay_episode INTEGER DEFAULT 1,
            video_quality TEXT DEFAULT 'Auto',
            remember_position INTEGER DEFAULT 1,
            subtitles TEXT DEFAULT 'English',
            autoplay_track INTEGER DEFAULT 1,
            shuffle INTEGER DEFAULT 0,
            repeat_mode TEXT DEFAULT 'Off',
            notifications_enabled INTEGER DEFAULT 1,
            toast_notifications INTEGER DEFAULT 1,
            new_content INTEGER DEFAULT 1,
            playback_notif INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)

    # 3. Create media_history with ON DELETE CASCADE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS media_history (
            history_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            media_type TEXT NOT NULL,
            tmdb_id INTEGER,
            title TEXT,
            poster_path TEXT,
            watched_at TEXT DEFAULT CURRENT_TIMESTAMP,
            duration INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)

    # 4. Create playlists (for music) with ON DELETE CASCADE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS playlists (
            playlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS playlist_tracks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            playlist_id INTEGER NOT NULL,
            media_item_id INTEGER NOT NULL,
            track_order INTEGER DEFAULT 0,
            added_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(playlist_id)   REFERENCES playlists(playlist_id) ON DELETE CASCADE,
            FOREIGN KEY(media_item_id) REFERENCES media_items(id)         ON DELETE CASCADE
        )
    """)

    # 5. Create local games (registered executables)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS local_games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            media_item_id INTEGER NOT NULL,
            exe_path TEXT NOT NULL,
            launch_args TEXT,
            last_launched_at TEXT,
            FOREIGN KEY(user_id)       REFERENCES users(user_id)       ON DELETE CASCADE,
            FOREIGN KEY(media_item_id) REFERENCES media_items(id)      ON DELETE CASCADE
        )
    """)

    # ==========================================
    # 6. INDEXES for performance
    # ==========================================
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_media_history_user   ON media_history(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_media_items_category ON media_items(category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_media_items_provider ON media_items(provider)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_fav_user        ON user_favorites(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_playback_user        ON playback_history(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_playlist_user        ON playlists(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_playlist_tracks       ON playlist_tracks(playlist_id)")

    conn.commit()