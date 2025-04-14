import logging

import requests
from requests.auth import HTTPBasicAuth

from slixmpp.exceptions import XMPPError
from config.xmpp_config import XMPPConfig

class ChatGroupsXMPP:
    def __init__(self, xmpp_client):
        self.xmpp_client = xmpp_client
        self.xmpp_client.add_event_handler("socketio_event", self.handle_socketio_event)

    def handle_socketio_event(self, event_data):
        """Handles events from Flask-SocketIO related to chat groups."""
        pass

    def create_chat_group(self, chat_id: str):
        """Create a new XMPP chat group (MUC room)."""
        endpoint = f"{XMPPConfig.EJABBERD_API_URL}/create_room"
        payload = {
            "room": chat_id,
            "service": XMPPConfig.MUC_SERVICE,
            "host": XMPPConfig.VHOST
        }
        response = requests.post(
            endpoint,
            json=payload,
            auth=HTTPBasicAuth(XMPPConfig.ADMIN_USER, XMPPConfig.ADMIN_PASSWORD),
            verify=False
        )
        if response.status_code == 200:
            logging.info(f"Room {chat_id}@{XMPPConfig.MUC_SERVICE} created successfully.")
        else:
            logging.error(f"Failed to create room {chat_id}@{XMPPConfig.MUC_SERVICE}: {response.text}")

    def delete_chat_group(self, chat_id: str):
        """Delete an XMPP chat group (MUC room)."""
        endpoint = f"{XMPPConfig.EJABBERD_API_URL}/destroy_room"
        payload = {
            "room": chat_id,
            "service": XMPPConfig.MUC_SERVICE
        }
        response = requests.post(
            endpoint,
            json=payload,
            auth=HTTPBasicAuth(XMPPConfig.ADMIN_USER, XMPPConfig.ADMIN_PASSWORD),
            verify=False
        )
        if response.status_code == 200:
            logging.info(f"Room {chat_id}@{XMPPConfig.MUC_SERVICE} destroyed successfully.")
        else:
            logging.error(f"Failed to destroy room {chat_id}@{XMPPConfig.MUC_SERVICE}: {response.text}")
