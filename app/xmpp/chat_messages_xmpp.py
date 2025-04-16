import logging
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException

from config.xmpp_config import XMPPConfig


class ChatMessagesXMPP:
    def __init__(self):
        pass

    @staticmethod
    def _post(endpoint: str, payload: dict) -> requests.Response:
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
    def send_message(
        user_id: str, to_id: str, message_type: str, subject: str, body: str
    ) -> bool:
        """
        Send a message to a user or chat room via ejabberd HTTP API.

        :param user_id: JID of the sender (bare or full JID)
        :param to_id: JID of the receiver - person or group
        :param message_type: Type of message (e.g., "chat", "groupchat", etc.)
        :param subject: Subject of the message
        :param body: Body of the message
        :return: True if message was sent successfully, False otherwise
        """
        to_jid = (
            f"{to_id}@{XMPPConfig.MUC_SERVICE}"
            if message_type == "groupchat"
            else f"{to_id}@{XMPPConfig.VHOST}"
        )
        from_jid = f"{user_id}@{XMPPConfig.VHOST}"

        endpoint = f"{XMPPConfig.EJABBERD_API_URL}/send_message"
        payload = {
            "type": message_type,
            "from": from_jid,
            "to": to_jid,
            "subject": subject or "",
            "body": body or "",
        }

        try:
            response = ChatMessagesXMPP._post(endpoint, payload)

            result = response.json()
            if result == 0:
                logging.info(f"📤 Sent message from {from_jid} to {to_jid}: {body}")
                return True
            else:
                logging.error(
                    f"❌ Failed to send message from {from_jid} to {to_jid}: {result}"
                )
                return False
        except RequestException:
            logging.error(f"❌ Failed to send message from {from_jid} to {to_jid}")
            return False
