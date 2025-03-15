from bson.objectid import ObjectId
from datetime import datetime, UTC
from .database_init import ChatServiceDatabase

class ChatMessages:
    def __init__(self, db: ChatServiceDatabase):
        # Access the "chat_messages" collection from the database
        self.chat_messages = db.get_database()["chat_messages"]


    def insert_message(self, chat_id: str, sender_id: str, content: str) -> dict:
        """
        Store a message in the database
        """
    
        message_data = {
            "chat_id": ObjectId(chat_id),
            "sender_id": sender_id,
            "content": content,
            "sentAt": datetime.now(UTC).replace(tzinfo=None, microsecond=0)  # Truncate microseconds
        }
        result = self.chat_messages.insert_one(message_data)
        message_data["_id"] = result.inserted_id
        return message_data
    

    def fetch_message(self, message_id: str) -> dict | None:
        """Retrieves a message by ID."""
        return self.chat_messages.find_one({"_id": ObjectId(message_id)})


    def fetch_messages(self, chat_id: str, skip: int, limit: int) -> list:
        """Retrieves paginated messages for a chat group."""
        cursor = self.chat_messages.find({"chat_id": ObjectId(chat_id)}).sort("sentAt", -1).skip(skip).limit(limit)
        return list(cursor)
    

    def update_message(self, message_id: str, new_content: str) -> bool:
        """Updates a message's content."""
        result = self.chat_messages.update_one(
            {"_id": ObjectId(message_id)},
            {"$set": {"content": new_content, "editedAt": datetime.now(UTC).replace(tzinfo=None, microsecond=0)}}
        )
        return result.modified_count > 0


    def delete_message(self, message_id: str) -> bool:
        """Deletes a message by ID."""
        result = self.chat_messages.delete_one({"_id": ObjectId(message_id)})
        return result.deleted_count > 0
