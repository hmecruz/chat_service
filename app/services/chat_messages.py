from bson.objectid import ObjectId
from app.database.chat_messages import ChatMessages

class ChatMessagesService:
    def __init__(self, chat_messages_dal: ChatMessages):
        """Business logic layer for chat messages."""
        self.chat_messages_dal = chat_messages_dal 


    def store_message(self, chat_id: str, sender_id: str, content: str) -> dict:
        """Validates and stores a new chat message."""
        if not content.strip():
            raise ValueError("Message content cannot be empty")

        message = self.chat_messages_dal.insert_message(ObjectId(chat_id), sender_id, content)

        if not message or "_id" not in message:
            raise RuntimeError("Failed to store message")

        return message


    def get_message(self, message_id: str) -> dict:
        """Retrieves a message by ID with validation."""
        message = self.chat_messages_dal.fetch_message(ObjectId(message_id))

        if not message:
            raise ValueError(f"Message with ID {message_id} not found")

        return message


    def get_messages(self, chat_id: str, page: int = 1, limit: int = 20) -> list:
        """Retrieves paginated messages for a chat group."""
        if page < 1 or limit < 1:
            raise ValueError("Page and limit must be greater than zero")

        skip = (page - 1) * limit
        return self.chat_messages_dal.fetch_messages(ObjectId(chat_id), skip, limit)


    def edit_message(self, message_id: str, new_content: str) -> dict:
        """Validates and updates a message's content."""
        if not new_content.strip():
            raise ValueError("New content cannot be empty")

        updated = self.chat_messages_dal.update_message(ObjectId(message_id), new_content)

        if not updated:
            raise RuntimeError("Failed to update message")

        return {"_id": message_id, "content": new_content}
    

    def delete_message(self, message_id: str) -> bool:
        """Deletes a message with verification."""
        deleted = self.chat_messages_dal.delete_message(ObjectId(message_id))

        if not deleted:
            raise ValueError(f"Message with ID {message_id} not found or already deleted")

        return True
