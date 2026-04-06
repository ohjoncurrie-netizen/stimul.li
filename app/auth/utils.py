import secrets


API_KEY_PREFIX = "stim_"


def generate_api_key() -> str:
    """Generate a high-entropy API key with the project prefix."""
    return f"{API_KEY_PREFIX}{secrets.token_urlsafe(32)}"
