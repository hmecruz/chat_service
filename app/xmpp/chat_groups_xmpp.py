import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException

from config.xmpp_config import XMPPConfig

from .logger import xmpp_logger


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
            xmpp_logger.info(f"✅ HTTP POST to {endpoint} succeeded.")
            return response
        except RequestException as e:
            xmpp_logger.exception(f"❌ HTTP request failed (POST {endpoint}): {e}")
            raise

    @staticmethod
    def create_chat_group(chat_id: str, users: list[str]) -> bool:
        """Create a new XMPP chat group (MUC room) with owners and members directly."""
        affiliations = []
        subscribers = []

        if users:
            affiliations.append(f"owner={users[0]}@{XMPPConfig.VHOST}")
            for user in users[1:]:
                affiliations.append(f"member={user}@{XMPPConfig.VHOST}")
                subscribers.append(f"{user}@{XMPPConfig.VHOST}={user}=messages")

        options = [
            {"name": "members_only", "value": "true"},
            {"name": "affiliations", "value": ";".join(affiliations)},
            {"name": "subscribers", "value": ";".join(subscribers)},
        ]

        xmpp_logger.debug(f"🔧 Creating group {chat_id} with options: {options}")
        return ChatGroupsXMPP.create_room_with_opts(chat_id, options)

    @staticmethod
    def create_room_with_opts(room: str, options: list[dict]) -> bool:
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
                xmpp_logger.info(f"✅ Room {room}@{XMPPConfig.MUC_SERVICE} created successfully.")
                return True
            else:
                xmpp_logger.error(f"❌ Failed to create room {room}@{XMPPConfig.MUC_SERVICE}: {result}")
                return False
        except RequestException:
            xmpp_logger.error(f"❌ Failed to create room {room}@{XMPPConfig.MUC_SERVICE}")
            return False

    @staticmethod
    def delete_chat_group(chat_id: str) -> bool:
        endpoint = f"{XMPPConfig.EJABBERD_API_URL}/destroy_room"
        payload = {
            "room": chat_id,
            "service": XMPPConfig.MUC_SERVICE,
        }

        try:
            response = ChatGroupsXMPP._post(endpoint, payload)
            result = response.json()
            if result == 0:
                xmpp_logger.info(f"🗑️ Room {chat_id}@{XMPPConfig.MUC_SERVICE} destroyed successfully.")
                return True
            else:
                xmpp_logger.error(f"❌ Failed to destroy room {chat_id}@{XMPPConfig.MUC_SERVICE}: {result}")
                return False
        except RequestException:
            xmpp_logger.error(f"❌ Failed to destroy room {chat_id}@{XMPPConfig.MUC_SERVICE}")
            return False

    @staticmethod
    def get_user_rooms(username: str) -> list[str]:
        endpoint = f"{XMPPConfig.EJABBERD_API_URL}/get_user_rooms"
        payload = {
            "user": username,
            "host": XMPPConfig.VHOST,
        }

        try:
            response = ChatGroupsXMPP._post(endpoint, payload)
            rooms = response.json()
            xmpp_logger.info(f"✅ User {username}@{XMPPConfig.VHOST} is in rooms: {rooms}")
            return rooms
        except RequestException:
            xmpp_logger.error(f"❌ Failed to get rooms for user {username}@{XMPPConfig.VHOST}")
            return []

    @staticmethod
    def get_room_occupants(room: str) -> list[dict]:
        endpoint = f"{XMPPConfig.EJABBERD_API_URL}/get_room_occupants"
        payload = {
            "room": room,
            "service": XMPPConfig.MUC_SERVICE,
        }

        try:
            response = ChatGroupsXMPP._post(endpoint, payload)
            occupants = response.json()
            xmpp_logger.info(f"✅ Occupants in room {room}@{XMPPConfig.MUC_SERVICE}: {occupants}")
            return occupants
        except RequestException:
            xmpp_logger.error(f"❌ Failed to get occupants for room {room}@{XMPPConfig.MUC_SERVICE}")
            return []
        
    def get_room_affiliated_usernames(self, chat_id: str) -> list[str]:
        """Fetch affiliated users (owners/members) from XMPP room."""
        endpoint = f"{XMPPConfig.EJABBERD_API_URL}/get_room_affiliations"
        payload = {
            "room": chat_id,
            "service": XMPPConfig.MUC_SERVICE,
        }

        try:
            response = ChatGroupsXMPP._post(endpoint, payload)
            affiliations = response.json()
            xmpp_logger.info(f"✅ Affiliations for room {chat_id}@{XMPPConfig.MUC_SERVICE}: {affiliations}")
            return affiliations
        except Exception as e:
            xmpp_logger.error(f"❌ Failed to retrieve affiliations for room {chat_id}: {e}")
            return []

    @staticmethod
    def set_room_affiliation(room: str, user: str, affiliation: str) -> bool:
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
                xmpp_logger.info(f"✅ Set affiliation '{affiliation}' for user {user}@{XMPPConfig.VHOST} in room {room}.")
                return True
            else:
                xmpp_logger.error(f"❌ Failed to set affiliation '{affiliation}' for user {user}@{XMPPConfig.VHOST} in room {room}: {result}")
                return False
        except RequestException:
            xmpp_logger.error(f"❌ Failed to set affiliation '{affiliation}' for user {user}@{XMPPConfig.VHOST} in room {room}")
            return False

    @staticmethod
    def add_user_to_room(room: str, user: str) -> bool:
        return ChatGroupsXMPP.set_room_affiliation(room, user, "member")

    @staticmethod
    def add_users_to_room(room: str, users: list[str]) -> bool:
        success = True
        for user in users:
            if not ChatGroupsXMPP.set_room_affiliation(room, user, "member"):
                xmpp_logger.error(f"❌ Failed to add user {user} to room {room}")
                success = False
        return success

    @staticmethod
    def remove_user_from_room(room: str, user: str) -> bool:
        return ChatGroupsXMPP.set_room_affiliation(room, user, "none")

    @staticmethod
    def remove_users_from_room(room: str, users: list[str]) -> bool:
        success = True
        for user in users:
            if not ChatGroupsXMPP.set_room_affiliation(room, user, "none"):
                xmpp_logger.error(f"❌ Failed to remove user {user} from room {room}")
                success = False
        return success
