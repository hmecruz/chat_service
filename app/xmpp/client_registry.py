from typing import Dict, Any

class XMPPClientRegistry:
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
