import logging
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException

from config.xmpp_config import XMPPConfig


class ChatGroupsXMPP:
    def __init__(self):
        pass

    @staticmethod
    def _post(endpoint: str, payload: dict) -> requests.Response:
        """Helper method for making HTTP POST requests."""
        try:
            response = requests.post(
                endpoint,
                json=payload,
                auth=HTTPBasicAuth(XMPPConfig.ADMIN_USER, XMPPConfig.ADMIN_PASSWORD),
                verify=False
            )
            response.raise_for_status()
            return response
        except RequestException as e:
            logging.exception(f"❌ HTTP request failed (POST {endpoint}): {e}")
            raise

    @staticmethod
    def create_chat_group(chat_id: str, users: list[str]) -> bool:
        """Create a new XMPP chat group (MUC room) with owners and members directly."""
        affiliations = []
        subscribers = []

        # First user is the owner
        if users:
            affiliations.append(f"owner={users[0]}@{XMPPConfig.VHOST}")
            # Set the remaining users as members
            for user in users[1:]:
                affiliations.append(f"member={user}@{XMPPConfig.VHOST}")
                subscribers.append(f"{user}@{XMPPConfig.VHOST}={user}=messages")

        options = [
            {"name": "members_only", "value": "true"},
            {"name": "affiliations", "value": ";".join(affiliations)},
            {"name": "subscribers", "value": ";".join(subscribers)},
        ]

        return ChatGroupsXMPP.create_room_with_opts(chat_id, options)

    @staticmethod
    def create_room_with_opts(room: str, options: list[dict]) -> bool:
        """Create an XMPP MUC room with custom options via ejabberd HTTP API."""
        endpoint = f"{XMPPConfig.EJABBERD_API_URL}/create_room_with_opts"
        payload = {
            "room": room,
            "service": XMPPConfig.MUC_SERVICE,
            "host": XMPPConfig.VHOST,
            "options": options,
        }

        try:
            response = ChatGroupsXMPP._post(endpoint, payload)
            result = response.json()

            if result == 0:
                logging.info(f"✅ Room {room}@{XMPPConfig.MUC_SERVICE} created successfully.")
                return True
            else:
                logging.error(f"❌ Failed to create room {room}@{XMPPConfig.MUC_SERVICE}: {result}")
                return False
        except RequestException:
            logging.error(f"❌ Failed to create room {room}@{XMPPConfig.MUC_SERVICE}")
            return False

    @staticmethod
    def delete_chat_group(chat_id: str) -> bool:
        """Delete an XMPP chat group (MUC room)."""
        endpoint = f"{XMPPConfig.EJABBERD_API_URL}/destroy_room"
        payload = {
            "room": chat_id,
            "service": XMPPConfig.MUC_SERVICE,
        }

        try:
            response = ChatGroupsXMPP._post(endpoint, payload)
            logging.info(f"🗑️ Room {chat_id}@{XMPPConfig.MUC_SERVICE} destroyed successfully.")
            return True
        except RequestException:
            logging.error(f"❌ Failed to destroy room {chat_id}@{XMPPConfig.MUC_SERVICE}")
            return False

    @staticmethod
    def get_user_rooms(username: str) -> list[str]:
        """Get the list of rooms where this user is an occupant."""
        endpoint = f"{XMPPConfig.EJABBERD_API_URL}/get_user_rooms"
        payload = {
            "user": username,
            "host": XMPPConfig.VHOST,
        }

        try:
            response = ChatGroupsXMPP._post(endpoint, payload)
            rooms = response.json()
            logging.info(f"✅ User {username}@{XMPPConfig.VHOST} is in rooms: {rooms}")
            return rooms
        except RequestException:
            logging.error(f"❌ Failed to get rooms for user {username}@{XMPPConfig.VHOST}")
            return []

    @staticmethod
    def get_room_occupants(room: str) -> list[dict]:
        """Get the list of occupants of a MUC room."""
        endpoint = f"{XMPPConfig.EJABBERD_API_URL}/get_room_occupants"
        payload = {
            "room": room,
            "service": XMPPConfig.MUC_SERVICE,
        }

        try:
            response = ChatGroupsXMPP._post(endpoint, payload)
            occupants = response.json()
            logging.info(f"✅ Occupants in room {room}@{XMPPConfig.MUC_SERVICE}: {occupants}")
            return occupants
        except RequestException:
            logging.error(f"❌ Failed to get occupants for room {room}@{XMPPConfig.MUC_SERVICE}")
            return []

    @staticmethod
    def set_room_affiliation(room: str, user: str, affiliation: str) -> bool:
        """Set a user's affiliation in a MUC room."""
        endpoint = f"{XMPPConfig.EJABBERD_API_URL}/set_room_affiliation"
        payload = {
            "room": room,
            "service": XMPPConfig.MUC_SERVICE,
            "user": user,
            "host": XMPPConfig.VHOST,
            "affiliation": affiliation,
        }

        try:
            response = ChatGroupsXMPP._post(endpoint, payload)
            result = response.json()

            if result == 0:
                logging.info(f"✅ Set affiliation '{affiliation}' for user {user}@{XMPPConfig.VHOST} in room {room}.")
                return True
            else:
                logging.error(f"❌ Failed to set affiliation '{affiliation}' for user {user}@{XMPPConfig.VHOST} in room {room}: {result}")
                return False
        except RequestException:
            logging.error(f"❌ Failed to set affiliation '{affiliation}' for user {user}@{XMPPConfig.VHOST} in room {room}")
            return False

    @staticmethod
    def add_user_to_room(room: str, user: str) -> bool:
        """Add a user to a MUC room by setting their affiliation to 'member'."""
        return ChatGroupsXMPP.set_room_affiliation(room, user, "member")

    @staticmethod
    def add_users_to_room(room: str, users: list[str]) -> bool:
        """Add multiple users to a MUC room by setting their affiliation to 'member'."""
        success = True
        for user in users:
            if not ChatGroupsXMPP.set_room_affiliation(room, user, "member"):
                logging.error(f"❌ Failed to add user {user} to room {room}")
                success = False
        return success

    @staticmethod
    def remove_user_from_room(room: str, user: str) -> bool:
        """Remove a user from a MUC room by setting their affiliation to 'none'."""
        return ChatGroupsXMPP.set_room_affiliation(room, user, "none")

    @staticmethod
    def remove_users_from_room(room: str, users: list[str]) -> bool:
        """Remove multiple users from a MUC room by setting their affiliation to 'none'."""
        success = True
        for user in users:
            if not ChatGroupsXMPP.set_room_affiliation(room, user, "none"):
                logging.error(f"❌ Failed to remove user {user} from room {room}")
                success = False
        return success
