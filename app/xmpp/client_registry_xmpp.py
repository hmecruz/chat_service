from typing import Dict, Any

from .chat_client import XMPPClient
from config.xmpp_config import *

class ClientRegistryXMPP:
    """In-memory registry to track active Slixmpp clients by user ID."""

    def __init__(self):
        self._clients: Dict[str, Any] = {}

    def register(self, user_id: str, client: Any) -> None:
        self._clients[user_id] = client

    def get_client(self, user_id: str) -> Any | None:
        return self._clients.get(user_id)

    def unregister(self, user_id: str) -> None:
        self._clients.pop(user_id, None)

    def all_users(self) -> list[str]:
        return list(self._clients.keys())

    def has_user(self, user_id: str) -> bool:
        return user_id in self._clients
    
    def missing_users(self, user_ids: list[str]) -> list[str]:
        """Return the list of user IDs not found in the registry."""
        return [uid for uid in user_ids if uid not in self._clients]

    def register_users(self, user_ids: list[tuple[str, str]]) -> None:
        """Register multiple users in the registry at once."""
        for user_id in user_ids:
            jid = f"{user_id[0]}@{XMPPConfig.VHOST}"
            password = user_id[1]
            self.register(user_id, XMPPClient(jid, password, use_certificate=False))