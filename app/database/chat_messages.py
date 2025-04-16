from datetime import datetime, UTC
from .database_init import ChatServiceDatabase

class ChatMessages:
    def __init__(self, db: ChatServiceDatabase):
        # Access the "chat_messages" collection from the database
        self.chat_messages = db.get_database()["chat_messages"]

    def insert_message(self, chat_id: str, sender_id: str, content: str) -> dict:
        """
        Store a message in the database.
        """
        message_data = {
            "chat_id": chat_id,  # No need for ObjectId conversion
            "sender_id": sender_id,
            "content": content,
            "sentAt": datetime.utcnow()  # If still necessary, make sure to use UTC
        }
        result = self.chat_messages.insert_one(message_data)
        return {"messageId": str(result.inserted_id)}

    def fetch_message(self, message_id: str) -> dict | None:
        """Retrieves a message by ID."""
        return self.chat_messages.find_one({"_id": message_id})

    def fetch_messages(self, chat_id: str, skip: int, limit: int, sort_by="sentAt", sort_order=-1) -> list | None:
        """Retrieves paginated messages for a chat group."""
        cursor = self.chat_messages.find({"chat_id": chat_id}).sort(sort_by, sort_order).skip(skip).limit(limit)
        return list(cursor)

    def update_message(self, message_id: str, new_content: str) -> bool:
        """Updates a message's content."""
        result = self.chat_messages.update_one(
            {"_id": message_id},
            {"$set": {"content": new_content, "editedAt": datetime.utcnow()}}  # Ensure UTC time if needed
        )
        return result.modified_count > 0

    def delete_message(self, message_id: str) -> bool:
        """Deletes a message by ID."""
        result = self.chat_messages.delete_one({"_id": message_id})
        return result.deleted_count > 0