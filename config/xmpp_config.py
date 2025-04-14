from .base_config import get_env_variable

class XMPPConfig:
    """Class to store XMPP configuration settings."""
    
    EJABBERD_API_URL = get_env_variable("EJABBERD_API_URL", "https://localhost:5443/api")
    ADMIN_USER = get_env_variable("ADMIN_USER", "admin@localhost")
    ADMIN_PASSWORD = get_env_variable("ADMIN_PASSWORD", "adminpassword")
    VHOST = get_env_variable("VHOST", "localhost")  # ejabberd virtual host for HTTP API calls
    MUC_SERVICE = get_env_variable("MUC_SERVICE", "conference.localhost")  # MUC service domain