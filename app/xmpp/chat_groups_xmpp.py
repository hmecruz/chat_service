import slixmpp
import logging
from slixmpp.exceptions import XMPPError
from slixmpp.plugins.xep_0045 import XEP_0045
from flask_socketio import emit

class ChatGroupsXMPP:
    def __init__(self, xmpp_client):
        self.xmpp_client = xmpp_client
        self.xmpp_client.add_event_handler("socketio_event", self.handle_socketio_event)

    def handle_socketio_event(self, event_data):
        """Handles events from Flask-SocketIO related to chat groups."""
        try:
            if event_data['event_type'] == 'create_chat':
                self.create_chat_group(event_data['chat_name'])
            elif event_data['event_type'] == 'add_users_to_chat':
                self.add_users_to_chat(event_data['chat_id'], event_data['user_ids'])
            elif event_data['event_type'] == 'remove_users_from_chat':
                self.remove_users_from_chat(event_data['chat_id'], event_data['user_ids'])
            elif event_data['event_type'] == 'delete_chat':
                self.delete_chat_group(event_data['chat_id'])
        except Exception as e:
            logging.error(f"Error handling SocketIO event: {e}")
            emit('error', {'error': str(e)})

    def create_chat_group(self, chat_name):
        """Create a new XMPP chat group (MUC room)."""
        try:
            # Join MUC (Multi-User Chat) room and create if not exists
            room_jid = f"{chat_name}@conference.{self.xmpp_client.boundjid.domain}"
            
            # XMPP MUC plugin: create the room (room creation will require administrative privileges)
            muc_plugin = self.xmpp_client.plugin['xep_0045']
            muc_plugin.create(room_jid, chat_name)

            logging.info(f"Chat group '{chat_name}' created successfully.")
            emit('chatGroupCreated', {'chatName': chat_name}, broadcast=True)
        except XMPPError as e:
            logging.error(f"Error creating chat group: {e}")
            emit('error', {'error': str(e)})

    def add_users_to_chat(self, chat_id, user_ids):
        """Add users to an existing XMPP chat group (MUC)."""
        try:
            room_jid = f"{chat_id}@conference.{self.xmpp_client.boundjid.domain}"
            
            # XMPP MUC plugin: Add users to the room
            muc_plugin = self.xmpp_client.plugin['xep_0045']
            for user_id in user_ids:
                muc_plugin.invite(room_jid, user_id)

            logging.info(f"Users {user_ids} added to chat group '{chat_id}'.")
            emit('usersAddedToChat', {'chatId': chat_id, 'userIds': user_ids}, broadcast=True)
        except XMPPError as e:
            logging.error(f"Error adding users to chat: {e}")
            emit('error', {'error': str(e)})

    def remove_users_from_chat(self, chat_id, user_ids):
        """Remove users from an existing XMPP chat group (MUC)."""
        try:
            room_jid = f"{chat_id}@conference.{self.xmpp_client.boundjid.domain}"
            
            # XMPP MUC plugin: Remove users from the room
            muc_plugin = self.xmpp_client.plugin['xep_0045']
            for user_id in user_ids:
                muc_plugin.kick(room_jid, user_id)

            logging.info(f"Users {user_ids} removed from chat group '{chat_id}'.")
            emit('usersRemovedFromChat', {'chatId': chat_id, 'userIds': user_ids}, broadcast=True)
        except XMPPError as e:
            logging.error(f"Error removing users from chat: {e}")
            emit('error', {'error': str(e)})

    def delete_chat_group(self, chat_id):
        """Delete an XMPP chat group (MUC room)."""
        try:
            room_jid = f"{chat_id}@conference.{self.xmpp_client.boundjid.domain}"
            
            # XMPP MUC plugin: Destroy the room (room destruction requires administrative privileges)
            muc_plugin = self.xmpp_client.plugin['xep_0045']
            muc_plugin.destroy(room_jid)

            logging.info(f"Chat group '{chat_id}' deleted successfully.")
            emit('chatGroupDeleted', {'chatId': chat_id}, broadcast=True)
        except XMPPError as e:
            logging.error(f"Error deleting chat group: {e}")
            emit('error', {'error': str(e)})

