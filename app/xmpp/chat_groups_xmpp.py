import logging
import requests
from requests.auth import HTTPBasicAuth

from slixmpp.exceptions import XMPPError
from config.xmpp_config import XMPPConfig


class ChatGroupsXMPP:
    def __init__(self):
        pass

    def handle_socketio_event(self, event_data):
        """Handles events from Flask-SocketIO related to chat groups."""
        pass

    @staticmethod
    def create_chat_group(chat_id: str, users: list[str]) -> bool:
        """Create a new XMPP chat group (MUC room) with owners and members directly."""
        
        # Prepare the affiliations and subscribers
        affiliations = []
        subscribers = []
        
        # First user is the owner
        if users:
            affiliations.append(f"owner={users[0]}@{XMPPConfig.VHOST}")
            # Set the remaining users as members
            for user in users[1:]:
                affiliations.append(f"member={user}@{XMPPConfig.VHOST}") # Members info
                subscribers.append(f"{user}@{XMPPConfig.VHOST}={user}=messages")  # Subscribers info

        # Define the options for room creation
        options = [
            {"name": "members_only", "value": "true"},
            {"name": "affiliations", "value": ";".join(affiliations)},
            {"name": "subscribers", "value": ";".join(subscribers)}
        ]
        
        # Create the room with the specified options
        return ChatGroupsXMPP.create_room_with_opts(chat_id, options)
    
    @staticmethod
    def create_room_with_opts(room: str, options: list[dict]) -> bool:
        """Create an XMPP MUC room with custom options via ejabberd HTTP API."""
        endpoint = f"{XMPPConfig.EJABBERD_API_URL}/create_room_with_opts"
        payload = {
            "room": room,
            "service": XMPPConfig.MUC_SERVICE,
            "host": XMPPConfig.VHOST,
            "options": options
        }

        try:
            response = requests.post(
                endpoint,
                json=payload,
                auth=HTTPBasicAuth(XMPPConfig.ADMIN_USER, XMPPConfig.ADMIN_PASSWORD),
                verify=False
            )
            response.raise_for_status()
            result = response.json()
            if result == 0:
                logging.info(f"✅ Room {room}@{XMPPConfig.MUC_SERVICE} created with options successfully.")
                return True
            else:
                logging.warning(f"⚠️ Room {room} creation returned non-zero result: {result}")
                return False

        except requests.RequestException as e:
            logging.error(f"❌ Failed to create room {room} with options: {e}")
            return False

    @staticmethod
    def delete_chat_group(chat_id: str):
        """Delete an XMPP chat group (MUC room)."""
        endpoint = f"{XMPPConfig.EJABBERD_API_URL}/destroy_room"
        payload = {
            "room": chat_id,
            "service": XMPPConfig.MUC_SERVICE
        }
        try:
            response = requests.post(
                endpoint,
                json=payload,
                auth=HTTPBasicAuth(XMPPConfig.ADMIN_USER, XMPPConfig.ADMIN_PASSWORD),
                verify=False
            )
            response.raise_for_status()
            logging.info(f"🗑️ Room {chat_id}@{XMPPConfig.MUC_SERVICE} destroyed successfully.")
            return True
        except requests.RequestException as e:
            logging.error(f"❌ Failed to destroy room {chat_id}@{XMPPConfig.MUC_SERVICE}: {e}")
            return False

    @staticmethod
    def get_user_rooms(username: str) -> list[str]:
        """Get the list of rooms where this user is an occupant."""
        endpoint = f"{XMPPConfig.EJABBERD_API_URL}/get_user_rooms"
        payload = {
            "user": username,
            "host": XMPPConfig.VHOST
        }
        try:
            response = requests.post(
                endpoint,
                json=payload,
                auth=HTTPBasicAuth(XMPPConfig.ADMIN_USER, XMPPConfig.ADMIN_PASSWORD),
                verify=False
            )
            response.raise_for_status()
            rooms = response.json()
            logging.info(f"✅ User {username}@{XMPPConfig.VHOST} is in rooms: {rooms}")
            return rooms
        except requests.RequestException as e:
            logging.error(f"❌ Failed to get user rooms for {username}: {e}")
            return []

    @staticmethod
    def get_room_occupants(room: str) -> list[dict]:
        """Get the list of occupants of a MUC room."""
        endpoint = f"{XMPPConfig.EJABBERD_API_URL}/get_room_occupants"
        payload = {
            "room": room,
            "service": XMPPConfig.MUC_SERVICE
        }
        try:
            response = requests.post(
                endpoint,
                json=payload,
                auth=HTTPBasicAuth(XMPPConfig.ADMIN_USER, XMPPConfig.ADMIN_PASSWORD),
                verify=False
            )
            response.raise_for_status()
            occupants = response.json()
            logging.info(f"✅ Occupants in room {room}@{XMPPConfig.MUC_SERVICE}: {occupants}")
            return occupants
        except requests.RequestException as e:
            logging.error(f"❌ Failed to get occupants of room {room}: {e}")
            return []
        
    def set_room_affiliation(room: str, user: str, affiliation: str) -> bool:
        """Set a user's affiliation in a MUC room."""
        endpoint = f"{XMPPConfig.EJABBERD_API_URL}/set_room_affiliation"
        payload = {
            "room": room,
            "service": XMPPConfig.MUC_SERVICE,
            "user": user,
            "host": XMPPConfig.VHOST,
            "affiliation": affiliation
        }
        try:
            response = requests.post(
                endpoint,
                json=payload,
                auth=HTTPBasicAuth(XMPPConfig.ADMIN_USER, XMPPConfig.ADMIN_PASSWORD),
                verify=False
            )
            response.raise_for_status()
            result = response.json()
            if result == 0:
                logging.info(f"✅ Set affiliation '{affiliation}' for user {user}@{XMPPConfig.VHOST} in room {room}.")
                return True
            else:
                logging.warning(f"⚠️ Failed to set affiliation '{affiliation}' for user {user}@{XMPPConfig.VHOST} in room {room}. Response: {result}")
                return False
        except requests.RequestException as e:
            logging.error(f"❌ Error setting affiliation '{affiliation}' for user {user}@{XMPPConfig.VHOST} in room {room}: {e}")
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