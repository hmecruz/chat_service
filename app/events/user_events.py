from flask import current_app, request, has_request_context
from flask_socketio import emit

from .logger import events_logger

class UserEvents:
    def __init__(self):
        self.user_service = current_app.config['user_service']

    def _emit_success(self, event_name, response, target_user_ids=None):
        """
        Emit success to specific user rooms, or fallback to broadcast (e.g., in tests).
        """
        if target_user_ids:
            for user_id in target_user_ids:
                emit(event_name, response, room=user_id)
        elif has_request_context() and hasattr(request, 'sid'):
            emit(event_name, response, room=request.sid)
        else:
            emit(event_name, response, broadcast=True)

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

        # Log the error event
        events_logger.error(f"Error: {message} | User: {user_id if user_id else 'N/A'}")

    # -----------------------------------------------------------------------------
    # Event: Get Chat List for a User
    # Channel: user/{userId}/chats
    # -----------------------------------------------------------------------------
    def handle_get_chat_list(self, data):
        """
        Expected payload (ChatListRequest):
            {
                "userId": "user123",
                "page": 1,
                "limit": 20
            }
        """
        try:
            user_id = data.get("userId")
            page = data.get("page")
            limit = data.get("limit")

            events_logger.info(f"Request to get chat list for user {user_id}. Page: {page}, Limit: {limit}")

            if not user_id or not isinstance(page, int) or not isinstance(limit, int):
                raise ValueError("Missing or invalid fields: userId, page, and limit are required")

            result = self.user_service.get_chat_list(user_id, page, limit)

            response = {
                "userId": user_id,
                "page": page,
                "limit": limit,
                "total": result["total"],
                "chats": result["chats"]
            }

            events_logger.info(f"Successfully fetched chat list for user {user_id}. Total chats: {result['total']}")
            self._emit_success('getUserChats', response, target_user_ids=[user_id])
            events_logger.info(f"Chat list for user {user_id}: {response['chats']}")
        
        except Exception as e:
            error_message = str(e)
            events_logger.error(f"Failed to handle get chat list for user {data.get('userId')}. Error: {error_message}")
            self._emit_error(error_message, user_id=data.get("userId"))
