from flask import current_app, request, has_request_context
from flask_socketio import emit

class ChatMessagesEvents:
    def __init__(self):
        self.chat_messages_service = current_app.config['chat_messages_service']
        self.chat_groups_service = current_app.config['chat_groups_service']

    def _emit_error(self, message, user_id=None, type="processing_error"):
        error_payload = {
            "type": type,
            "message": message
        }
        if user_id:
            emit('error', error_payload, room=user_id)
        elif has_request_context() and hasattr(request, 'sid'):
            emit('error', error_payload, room=request.sid)
        else:
            emit('error', error_payload, broadcast=True)

    def _emit_to_chat_users(self, event_name, payload, chat_id, exclude_user_id=None):
        """Emit to each chat user in their own room (excluding one if specified)."""
        try:
            users = self.chat_groups_service.get_chat_users(chat_id)
            for user_id in users:
                if user_id != exclude_user_id:
                    emit(event_name, payload, room=user_id)
        except Exception as e:
            self._emit_error(f"Failed to fetch users for chatId={chat_id}: {str(e)}")

    # -----------------------------------------------------------------------------
    # Event: Send Message
    # Channel: chat/{chatId}/message
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

            if not chat_id or not sender_id or not content:
                raise ValueError("Invalid request: chatId, senderId, and content are required fields")
            
            new_message = self.chat_messages_service.send_message(chat_id, sender_id, content)

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
            self._emit_to_chat_users('receiveMessage', response, chat_id, exclude_user_id=sender_id)

        except Exception as e:
            self._emit_error(str(e), user_id=data.get('senderId'))
            
    # -----------------------------------------------------------------------------
    # Event: Edit Message
    # Channel: chat/{chatId}/message/edit
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

            updated_message = self.chat_messages_service.edit_message(message_id, new_content)

            response = {
                "chatId": chat_id,
                "messageId": str(updated_message["_id"]),
                "newContent": updated_message["content"],
                "editedAt": updated_message.get("editedAt")
            }
            self._emit_to_chat_users('messageEdited', response, chat_id)

        except Exception as e:
            self._emit_error(str(e))


    # -----------------------------------------------------------------------------
    # Event: Delete Message
    # Channel: chat/{chatId}/message/delete
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

            self.chat_messages_service.delete_message(message_id)

            response = {
                "chatId": chat_id,
                "messageId": message_id,
            }
            self._emit_to_chat_users('messageDeleted', response, chat_id)

        except Exception as e:
            self._emit_error(str(e))
            
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

            messages_list = self.chat_messages_service.get_messages(chat_id, page, limit)
            total = len(messages_list)

            formatted_messages = [{
                "messageId": str(msg["_id"]),
                "senderId": msg["sender_id"],
                "content": msg["content"],
                "sentAt": msg["sentAt"]
            } for msg in messages_list]

            response = {
                "chatId": chat_id,
                "page": page,
                "limit": limit,
                "total": total,
                "messages": formatted_messages
            }

            if has_request_context() and hasattr(request, 'sid'):
                emit('messageHistoryResponse', response, room=request.sid)
            else:
                emit('messageHistoryResponse', response)

        except Exception as e:
            self._emit_error(str(e))