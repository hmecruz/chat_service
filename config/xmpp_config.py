from config.base_config import get_env_variable

class XmppConfig:
    JID = get_env_variable("XMPP_JID", "user@example.com")
    PASSWORD = get_env_variable("XMPP_PASSWORD", "password")
    WEBSOCKET_URL = get_env_variable("XMPP_WEBSOCKET_URL", "wss://127.0.0.1:8080")