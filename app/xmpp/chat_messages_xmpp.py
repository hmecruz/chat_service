import slixmpp
import logging
from slixmpp.exceptions import XMPPError
from flask_socketio import emit
from slixmpp.plugins.xep_0030 import XEP_0030
from slixmpp.plugins.xep_0060 import XEP_0060
from slixmpp.plugins.xep_0045 import XEP_0045

class ChatMessagesXMPP:
    def __init__(self, xmpp_client):
        self.xmpp_client = xmpp_client
        self.xmpp_client.add_event_handler("socketio_event", self.handle_socketio_event)

    def handle_socketio_event(self, event_data):
        """Handles events from Flask-SocketIO related to chat messages."""
        try:
            if event_data['event_type'] == 'send_message':
                self.send_message(event_data['chat_id'], event_data['sender_id'], event_data['content'])
            elif event_data['event_type'] == 'edit_message':
                self.edit_message(event_data['chat_id'], event_data['message_id'], event_data['new_content'])
            elif event_data['event_type'] == 'delete_message':
                self.delete_message(event_data['chat_id'], event_data['message_id'])
        except Exception as e:
            logging.error(f"Error handling SocketIO event: {e}")
            emit('error', {'error': str(e)})

    def send_message(self, chat_id, sender_id, content):
        """Send a message to an XMPP chat room (MUC)."""
        try:
            room_jid = f"{chat_id}@conference.{self.xmpp_client.boundjid.domain}"
            message = self.xmpp_client.make_message(mto=room_jid, mbody=content, mtype='groupchat')
            message['from'] = self.xmpp_client.boundjid.bare
            message.send()

            # Broadcast to the connected clients
            response = {
                "chatId": chat_id,
                "senderId": sender_id,
                "content": content,
                "sentAt": message['timestamp'],
            }
            logging.info(f"Message sent to {room_jid}: {content}")
            emit('receiveMessage', response, broadcast=True)
        except XMPPError as e:
            logging.error(f"Error sending message: {e}")
            emit('error', {'error': str(e)})

    def edit_message(self, chat_id, message_id, new_content):
        """Edit a previously sent message in a chat room (XMPP)."""
        try:
            # This assumes you have a method to store and update messages in your database
            # In XMPP, editing messages is not a built-in feature, so you may need to implement
            # a custom solution (e.g., deleting the old message and sending a new one).
            room_jid = f"{chat_id}@conference.{self.xmpp_client.boundjid.domain}"
            
            # Find the original message using the message_id (in your database, for example)
            original_message = self.get_message_by_id(message_id)  # Fetch the original message from DB

            if original_message:
                # Delete the original message and send a new one with updated content
                self.delete_message(chat_id, message_id)  # Delete old message
                self.send_message(chat_id, original_message['sender_id'], new_content)  # Send new message

                logging.info(f"Message with ID {message_id} edited successfully.")
                response = {
                    "chatId": chat_id,
                    "messageId": message_id,
                    "newContent": new_content,
                }
                emit('messageEdited', response, broadcast=True)
            else:
                logging.error(f"Message ID {message_id} not found.")
                emit('error', {'error': 'Message not found'})
        except XMPPError as e:
            logging.error(f"Error editing message: {e}")
            emit('error', {'error': str(e)})

    def delete_message(self, chat_id, message_id):
        """Delete a message from a chat room (XMPP)."""
        try:
            # Deleting a message in XMPP rooms (MUC) is not directly supported, so it would likely be
            # handled through custom logic (e.g., informing the group of the message deletion).
            # Optionally, you may choose to just remove the message from the UI by notifying all participants.
            
            room_jid = f"{chat_id}@conference.{self.xmpp_client.boundjid.domain}"
            
            # Broadcast a "message deleted" notification (You can implement more custom logic here)
            response = {
                "chatId": chat_id,
                "messageId": message_id,
            }
            logging.info(f"Message with ID {message_id} deleted successfully.")
            emit('messageDeleted', response, broadcast=True)
        except XMPPError as e:
            logging.error(f"Error deleting message: {e}")
            emit('error', {'error': str(e)})

    def get_message_by_id(self, message_id):
        """Fetch a message from the database using the message_id."""
        # This is a placeholder for your database query. Replace it with your actual method to fetch messages.
        # For example, you might have a database service that handles fetching messages.
        return {
            "message_id": message_id,
            "sender_id": "user1",  # Replace with actual sender_id
            "content": "Original message content",  # Replace with actual content
        }
