from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class MediaItem:
    """Standardized media item across all providers."""
    internal_id: str
    provider: str
    external_id: str
    category: str  # "movie", "tv", "music", "game"
    title: str
    description: str = ""
    artwork_url: Optional[str] = None
    backdrop_url: Optional[str] = None
    release_date: Optional[str] = None
    rating: Optional[float] = None
    genres: List[str] = field(default_factory=list)
    
    # Playback-specific
    playable: bool = False
    playback_url: Optional[str] = None
    playback_type: Optional[str] = None  # "video_stream", "youtube", "audio_stream", "html5_game", "local_exe"
    
    # Provider-specific metadata (store raw for detail views)
    raw_metadata: dict = field(default_factory=dict)