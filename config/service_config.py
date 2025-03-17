from .base_config import get_env_variable

class ServiceConfig:
    """Service-related configurations."""
    API_KEY = get_env_variable("API_KEY", "default_api_key")