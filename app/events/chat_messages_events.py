from flask import current_app
from flask_socketio import emit

class ChatMessagesEvents:
    def __init__(self, xmpp_client):
        self.chat_messages_service = current_app.config['chat_messages_service']
        self.xmpp_client = xmpp_client

    # -----------------------------------------------------------------------------
    # Event: Send Message
    # Channel: chat/{chatId}/message
    # Publish OperationId: sendMessage
    # Subscribe OperationId: receiveMessage
    # -----------------------------------------------------------------------------
    def handle_send_message(self, data):
        """
        Expected payload (SendMessageRequest):
          {
            "chatId": "chat123",
            "senderId": "user1",
            "content": "Hello, team!"
          }
        """
        try:
            chat_id = data.get('chatId')
            sender_id = data.get('senderId')
            content = data.get('content')
            
            # Store the message using the service layer
            new_message = self.chat_messages_service.store_message(chat_id, sender_id, content)
            
            # Prepare the event payload according to SendMessageEvent
            response = {
                "chatId": chat_id,
                "page": 1,            
                "limit": 1,
                "total": 1,
                "messages": [{
                    "messageId": str(new_message["_id"]),
                    "senderId": new_message["sender_id"],
                    "content": new_message["content"],
                    "sentAt": new_message["sentAt"]
                }]
            }
            emit('receiveMessage', response, broadcast=True)
        except Exception as e:
            emit('error', {'error': str(e)})

    # -----------------------------------------------------------------------------
    # Event: Edit Message
    # Channel: chat/{chatId}/message/edit
    # Publish OperationId: editMessage
    # Subscribe OperationId: messageEdited
    # -----------------------------------------------------------------------------
    def handle_edit_message(self, data):
        """
        Expected payload (EditMessageRequest):
          {
            "chatId": "chat123",
            "messageId": "msg567",
            "newContent": "Hello, everyone!"
          }
        """
        try:
            chat_id = data.get('chatId')
            message_id = data.get('messageId')
            new_content = data.get('newContent')
            
            # Update the message via the service layer
            updated_message = self.chat_messages_service.edit_message(message_id, new_content)

            # Construct the event payload per EditMessageEvent
            response = {
                "chatId": chat_id,
                "messageId": str(updated_message["_id"]),
                "newContent": updated_message["content"],
                "editedAt": updated_message.get("editedAt") #get the edited at field.
            }
            emit('messageEdited', response, broadcast=True)
        except Exception as e:
            emit('error', {'error': str(e)})

    # -----------------------------------------------------------------------------
    # Event: Delete Message
    # Channel: chat/{chatId}/message/delete
    # Publish OperationId: deleteMessage
    # Subscribe OperationId: messageDeleted
    # -----------------------------------------------------------------------------
    def handle_delete_message(self, data):
        """
        Expected payload (DeleteMessageRequest):
          {
            "chatId": "chat123",
            "messageId": "msg567"
          }
        """
        try:
            chat_id = data.get('chatId')
            message_id = data.get('messageId')
            
            # Delete the message using the service layer
            self.chat_messages_service.delete_message(message_id)
            
            # Prepare the event payload per DeleteMessageEvent
            response = {
                "chatId": chat_id,
                "messageId": message_id,
            }
            emit('messageDeleted', response, broadcast=True)
        except Exception as e:
            emit('error', {'error': str(e)})

    # -----------------------------------------------------------------------------
    # Event: Request Message History
    # Channel: chat/{chatId}/message/history
    # Publish OperationId: requestMessageHistory
    # -----------------------------------------------------------------------------
    def handle_message_history(self, data):
        """
        Expected payload (MessageHistoryRequest):
          {
            "chatId": "chat123",
            "page": 1,
            "limit": 20
          }
        """
        try:
            chat_id = data.get('chatId')
            page = data.get('page', 1)
            limit = data.get('limit', 20)
            
            # Retrieve paginated messages using the service layer
            messages_list = self.chat_messages_service.get_messages(chat_id, page, limit)
            
            
            total = len(messages_list)  # Total messages in message_list
            
            # Format each message for the response
            formatted_messages = []
            for msg in messages_list:
                formatted_messages.append({
                    "messageId": str(msg["_id"]),
                    "senderId": msg["sender_id"],
                    "content": msg["content"],
                    "sentAt": msg["sentAt"]
                })
            
            response = {
                "chatId": chat_id,
                "page": page,
                "limit": limit,
                "total": total,
                "messages": formatted_messages
            }
            # Emit a response event for message history; you can name this as required.
            emit('messageHistoryResponse', response)
        except Exception as e:
            emit('error', {'error': str(e)})