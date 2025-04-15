from ..utils.validators import validate_id, validate_message_content
from ..database.chat_messages import ChatMessages

class ChatMessagesService:
    def __init__(self, chat_messages_dal: ChatMessages):
        """Business logic layer for chat messages."""
        self.chat_messages_dal = chat_messages_dal 


    def store_message(self, chat_id: str, sender_id: str, content: str) -> dict:
        """Validates and stores a new chat message."""
        validate_id(chat_id)
        validate_id(sender_id)
        validate_message_content(content)
        
        message_id = self.chat_messages_dal.insert_message(chat_id, sender_id, content)
        if not message_id:
            raise RuntimeError("Failed to store message")
        
        message = self.chat_messages_dal.fetch_message(message_id)
        if not message:
            raise RuntimeError("Failed to retrieve stored message")
        
        if str(message["chat_id"]) != chat_id:
            raise RuntimeError("Chat ID mismatch in stored message")
        if message["sender_id"] != sender_id:
            raise RuntimeError("Sender ID mismatch in stored message")
        if message["content"] != content:
            raise RuntimeError("Content mismatch in stored message")
        
        return message


    def get_message(self, message_id: str) -> dict:
        """Retrieves a message by ID with validation."""
        validate_id(message_id)

        message = self.chat_messages_dal.fetch_message(message_id)
        if not message:
            raise ValueError(f"Message with ID {message_id} not found")
        
        if str(message["_id"]) != message_id:
            raise RuntimeError("Message ID mismatch in retrieved message")
        
        return message


    def get_messages(self, chat_id: str, page: int = 1, limit: int = 20) -> list:
        """Retrieves paginated messages for a chat group."""
        validate_id(chat_id)
        if page < 1 or limit < 1:
            raise ValueError("Page and limit must be greater than zero")
        
        skip = (page - 1) * limit
        return self.chat_messages_dal.fetch_messages(chat_id, skip, limit)


    def edit_message(self, chat_id: str, message_id: str, new_content: str) -> dict:
        """Validates and updates a message's content."""
        validate_id(chat_id)
        validate_id(message_id)
        validate_message_content(new_content)
        
        updated = self.chat_messages_dal.update_message(message_id, new_content)
        if not updated:
            raise RuntimeError("Failed to update message")
        
        update_message = self.chat_messages_dal.fetch_message(message_id)
        
        if not update_message:
            raise RuntimeError("Failed to retrieve updated message")
        
        if str(update_message["_id"]) != message_id:
            raise RuntimeError("Message ID mismatch in updated")
        if update_message["chat_id"] != chat_id:
            raise RuntimeError("Chat ID mismatch in updated message")
        if update_message["content"] != new_content:
            raise RuntimeError("Content mismatch in updated message")
        if update_message["editedAt"] is None:
            raise RuntimeError("Missing editedAt timestamp in updated message")

        return update_message
        

    def delete_message(self, chat_id: str, message_id: str) -> bool:
        """Deletes a message with verification."""
        validate_id(chat_id)
        validate_id(message_id)
        
        deleted = self.chat_messages_dal.delete_message(message_id)

        if not deleted:
            raise ValueError(f"Message with ID {message_id} not found or already deleted")
        
        # Confirm deletion
        message = self.chat_messages_dal.fetch_message(message_id)
        if message is not None:
            raise RuntimeError("Message still exists after deletion")

        return True
