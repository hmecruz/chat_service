import logging
import requests
from requests.auth import HTTPBasicAuth

from config.xmpp_config import XMPPConfig

class ChatMessagesXMPP:
    def __init__(self):
        pass

    def handle_socketio_event(self, event_data):
        """Handles events from Flask-SocketIO related to chat messages."""
        pass

    @staticmethod
    def send_message(user_id: str, to_id: str, message_type: str, subject: str, body: str) -> bool:
        """
        Send a message to a user or chat room via ejabberd HTTP API.

        :param user_id: JID of the sender (bare or full JID)
        :param to_id: JID of the receiver - person or group
        :param message_type: Type of message (e.g., "chat", "groupchat", etc.)
        :param subject: Subject of the message
        :param body: Body of the message
        :return: True if message was sent successfully, False otherwise
        """
        endpoint = f"{XMPPConfig.EJABBERD_API_URL}/send_message"
        payload = {
            "type": message_type, # e.g., "chat" or "groupchat"
            "from": f"{user_id}@{XMPPConfig.VHOST}",
            "to": f"{to_id}@{XMPPConfig.MUC_SERVICE}",
            "subject": subject,
            "body": body
        }

        response = requests.post(
            endpoint,
            json=payload,
            auth=HTTPBasicAuth(XMPPConfig.ADMIN_USER, XMPPConfig.ADMIN_PASSWORD),
            verify=False
        )

        if response.status_code == 200:
            result = response.json()
            if result == 0:
                logging.info(f"📤 Sent message from {user_id} to {to_id}: {body}")
                return True
            else:
                logging.error(f"❌ Failed to send message from {user_id} to {to_id}: {result}")
                response.raise_for_status()
        else:
            logging.error(f"❌ Failed to send message from {user_id} to {to_id}: {response.text}")
            response.raise_for_status()