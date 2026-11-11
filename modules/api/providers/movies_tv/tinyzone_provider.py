"""TinyZone Provider - DISABLED. Unauthorized streaming site."""
from modules.api.core.exceptions import ProviderUnauthorized

class TinyZoneProvider:
    NAME = "TinyZone"
    CATEGORY = "movies_tv"
    
    def __init__(self):
        raise ProviderUnauthorized(
            self.NAME,
            "tinyzone.org provides no authorized public API. Integrating it would violate "
            "the app's policy against unauthorized streaming and copyright circumvention."
        )