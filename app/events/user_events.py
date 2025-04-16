from flask import current_app, request, has_request_context
from flask_socketio import emit  

class UserEvents:
    def __init__(self):
        self.user_service = current_app.config['user_service']

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
            emit('chatList', response, room=user_id)

        except Exception as e:
            self._emit_error(str(e), user_id=data.get("userId"))
