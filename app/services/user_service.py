class UserService:
    def __init__(self):
        pass

    def get_chat_list(self, user_id: str, page: int = 1, limit: int = 20) -> dict:
        """
        Retrieves a paginated list of chat groups for a user.
        
        Args:
            user_id (str): The ID of the user.
            page (int): The page number for pagination.
            limit (int): The number of items per page.
        
        Returns:
            dict: A dictionary containing the total number of chats and the list of chat groups.
        """
        # Placeholder for actual implementation
        return {
            "total": 100, # Length of the chat list
            "chats": [
                {"chat_id": "chat1", "name": "Chat Group 1"},
                {"chat_id": "chat2", "name": "Chat Group 2"}
            ]
        }