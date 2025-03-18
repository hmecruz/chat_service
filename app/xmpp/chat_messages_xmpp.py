import logging

class ChatMessagesXMPP:
    """Handles messaging in XMPP group chats."""
    
    def __init__(self, xmpp_client):
        self.xmpp_client = xmpp_client

    async def send_group_message(self, room_jid: str, message: str):
        """Sends a message to the group chat."""
        try:
            msg = self.xmpp_client.Message()
            msg['to'] = room_jid
            msg['type'] = 'groupchat'
            msg['body'] = message
            msg.send()
            logging.info(f"Sent message to {room_jid}: {message}")
        except Exception as e:
            logging.error(f"Error sending group message: {e}")
            raise Exception("Failed to send group message")
