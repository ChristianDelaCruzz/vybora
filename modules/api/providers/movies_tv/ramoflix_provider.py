"""RamoFlix Provider - DISABLED. Unauthorized and flagged as malicious."""
from modules.api.core.exceptions import ProviderUnauthorized

class RamoflixProvider:
    NAME = "RamoFlix"
    CATEGORY = "movies_tv"
    
    def __init__(self):
        raise ProviderUnauthorized(
            self.NAME,
            "ramoflix.net is flagged as a phishing/malware site by 17+ security vendors "
            "and provides no authorized API or embedding method."
        )