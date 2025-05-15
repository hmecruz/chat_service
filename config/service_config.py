from .base_config import get_env_variable

class ServiceConfig:
    """Service-related configurations."""
    FLASK_HOST = get_env_variable("FLASK_HOST", "localhost")
    FLASK_PORT = get_env_variable("FLASK_PORT", 5000)
    API_KEY = get_env_variable("API_KEY", "default_api_key")
    JWT_SECRET_KEY = get_env_variable("JWT_SECRET_KEY")