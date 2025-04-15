from flask import current_app
from flask_socketio import emit  

class UserEvents:
    def __init__(self):
        self.user_service = current_app.config['user_service']

    # -----------------------------------------------------------------------------
    # Event: Get Chat List for a User
    # Channel: user/{userId}/chats
    # Publish OperationId: getChatList
    # Subscribe OperationId: chatList
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
                raise ValueError("Missing required fields: userId, page, and limit are required")

            result = self.user_service.get_chat_list(user_id, page, limit)

            response = {
                "userId": user_id,
                "page": page,
                "limit": limit,
                "total": result["total"],
                "chats": result["chats"]
            }
            emit('chatList', response)
        except Exception as e:
            emit('error', {'error': str(e)})