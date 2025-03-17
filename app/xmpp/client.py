import asyncio
import logging
import slixmpp
from slixmpp.exceptions import IqError, IqTimeout
from flask import current_app
from datetime import datetime, timezone

# Import your DAL and service layers
from app.database.database_init import ChatServiceDatabase
from app.database.chat_groups import ChatGroups
from app.database.chat_messages import ChatMessages
from app.services.chat_groups_services import ChatGroupsService
from app.services.chat_messages_services import ChatMessagesService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)-8s %(message)s')

class ChatClient(slixmpp.ClientXMPP):
    def __init__(self, jid, password, websocket_url, db_instance):
        super().__init__(jid, password)
        self.websocket_url = websocket_url
        self.db_instance = db_instance

        # Register XMPP event handlers
        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message)
        self.add_event_handler("disconnected", self.disconnected)

        # Register plugins for XMPP functionalities
        self.register_plugin('xep_0030')  # Service Discovery
        self.register_plugin('xep_0199')  # XMPP Ping
        self.register_plugin('xep_0045')  # Multi-User Chat (MUC)

        # Example: register MUC event handlers for a test room.
        self.add_event_handler("muc::testroom@conference.localhost::got_presence", self.muc_presence)
        self.add_event_handler("muc::testroom@conference.localhost::message", self.muc_message)

    async def session_start(self, event):
        """Called when the XMPP session is started."""
        self.send_presence()
        await self.get_roster()
        logging.info("XMPP session started")
        # Optionally join a default MUC room (adjust as needed)
        try:
            await self.plugin['xep_0045'].join_muc('testroom@conference.localhost', 'MyNick')
            logging.info("Joined MUC testroom@conference.localhost")
        except IqError as err:
            logging.error("Could not join MUC: %s", err.iq['error']['text'])
        except IqTimeout:
            logging.error("No response from MUC server.")

    def message(self, msg):
        """Handle direct XMPP messages."""
        if msg['type'] in ('chat', 'normal'):
            logging.info("Received message: %s from %s", msg['body'], msg['from'])
            # Process direct messages if necessary

    def muc_presence(self, presence):
        logging.info("MUC presence: %s - %s", presence['from'], presence.get('type', 'available'))

    def muc_message(self, msg):
        if msg['type'] == 'groupchat':
            logging.info("MUC message: %s from %s", msg['body'], msg['from'])

    def disconnected(self, event):
        logging.info("Disconnected from XMPP server.")

    # -------------------------------
    # Chat Group Functionalities
    # -------------------------------

    async def create_chat_group(self, group_name, users):
        """
        Create a new chat group (requires at least 2 users).
        """
        if len(users) < 2:
            raise ValueError("A chat group must have at least 2 users.")
        chat_group = self.chat_groups_service.create_chat_group(group_name, users)
        logging.info("Chat group created: %s", chat_group)
        return chat_group

    async def add_users_to_group(self, chat_id, user_ids):
        """Add users to an existing chat group."""
        result = self.chat_groups_service.add_users_to_chat(chat_id, user_ids)
        logging.info("Added users %s to chat group %s", user_ids, chat_id)
        return result

    async def remove_users_from_group(self, chat_id, user_ids):
        """Remove users from an existing chat group."""
        result = self.chat_groups_service.remove_users_from_chat(chat_id, user_ids)
        logging.info("Removed users %s from chat group %s", user_ids, chat_id)
        return result

    async def delete_chat_group(self, chat_id):
        """Delete a chat group."""
        result = self.chat_groups_service.delete_chat_group(chat_id)
        logging.info("Deleted chat group %s: %s", chat_id, result)
        return result

    # -------------------------------
    # Chat Message Functionalities
    # -------------------------------

    async def send_chat_message(self, chat_id, sender_id, content):
        """Send a new chat message."""
        new_message = self.chat_messages_service.store_message(chat_id, sender_id, content)
        logging.info("Sent message: %s", new_message)
        return new_message

    async def edit_chat_message(self, message_id, new_content):
        """Edit an existing chat message."""
        updated = self.chat_messages_service.edit_message(message_id, new_content)
        logging.info("Edited message %s: %s", message_id, updated)
        return updated

    async def delete_chat_message(self, message_id):
        """Delete a chat message."""
        result = self.chat_messages_service.delete_message(message_id)
        logging.info("Deleted message %s: %s", message_id, result)
        return result

    def get_user_chats(self, user_id, page=1, limit=20):
        """Retrieve the list of chat groups for a specific user."""
        chats = self.chat_groups_service.get_chat_groups_for_user(user_id, page, limit)
        logging.info("Retrieved chats for user %s: %s", user_id, chats)
        return chats

    def get_chat_history(self, chat_id, page=1, limit=20):
        """Retrieve previous messages from a specific chat group."""
        messages = self.chat_messages_service.get_messages(chat_id, page, limit)
        logging.info("Retrieved messages for chat %s: %s", chat_id, messages)
        return messages

    # -------------------------------
    # XMPP-Specific Methods
    # -------------------------------

    async def send_muc_message(self, room_jid, message):
        """
        Send a groupchat message to a specified room.
        """
        msg = self.Message()
        msg['to'] = room_jid
        msg['type'] = 'groupchat'
        msg['body'] = message
        msg.send()
        logging.info("Sent MUC message to %s: %s", room_jid, message)

# -----------------------------------------------------------------------------
# Example Usage
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    # Load your database connection (ChatServiceDatabase) appropriately.
    db = ChatServiceDatabase()
    
    # Create an instance of ChatClient with your XMPP credentials, WebSocket URL, and database instance.
    xmpp_client = ChatClient('user@example.com', 'password', 'wss://127.0.0.1:8080', db)
    
    # Connect to the XMPP server and process events
    xmpp_client.connect()
    xmpp_client.process(forever=True)
