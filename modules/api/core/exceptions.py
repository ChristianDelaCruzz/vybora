class ProviderError(Exception):
    """Base exception for all provider-related errors."""
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(self.message)

class ProviderUnavailable(ProviderError):
    def __init__(self, provider: str):
        super().__init__("PROVIDER_UNAVAILABLE", f"{provider} is currently unavailable.")

class ProviderUnauthorized(ProviderError):
    def __init__(self, provider: str, reason: str = "No authorized integration method found."):
        super().__init__("PROVIDER_UNAUTHORIZED", f"{provider} cannot be integrated: {reason}")

class InvalidResponse(ProviderError):
    def __init__(self, provider: str, details: str):
        super().__init__("INVALID_RESPONSE", f"{provider} returned invalid data: {details}")