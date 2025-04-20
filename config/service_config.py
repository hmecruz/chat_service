from .base_config import get_env_variable

class ServiceConfig:
    """Service-related configurations."""
    API_KEY = get_env_variable("API_KEY", "default_api_key")
    HOST = get_env_variable("HOST", "localhost")
    PORT = get_env_variable("PORT", 5000)
    JWT_SECRET_KEY = get_env_variable("JWT_SECRET_KEY")