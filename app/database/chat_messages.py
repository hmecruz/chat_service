from bson.objectid import ObjectId
from bson.errors import InvalidId
from datetime import datetime, UTC

from .database_init import ChatServiceDatabase

from .logger import database_logger

class ChatMessages:
    def __init__(self, db: ChatServiceDatabase):
        # Access the "chat_messages" collection from the database
        self.chat_messages = db.get_database()["chat_messages"]

    def insert_message(self, chat_id: str, sender_id: str, content: str) -> dict:
        """Store a message in the database."""
        message_data = {
            "chat_id": chat_id,
            "sender_id": sender_id,
            "content": content,
            "sentAt": datetime.now(UTC).replace(tzinfo=None, microsecond=0)
        }
        result = self.chat_messages.insert_one(message_data)
        database_logger.info(f"Inserted message from sender '{sender_id}' into chat '{chat_id}' with ID {result.inserted_id}.")
        return {"messageId": str(result.inserted_id)}

    def fetch_message(self, message_id: str) -> dict | None:
        """Retrieve a message by ID."""
        try:
            obj_id = ObjectId(message_id)
        except InvalidId:
            database_logger.warning(f"Invalid ObjectId for message fetch: {message_id}")
            return None

        message = self.chat_messages.find_one({"_id": obj_id})
        if message:
            database_logger.info(f"Fetched message with ID {message_id}.")
        else:
            database_logger.info(f"No message found with ID {message_id}.")
        return message

    def fetch_messages(self, chat_id: str, skip: int, limit: int, sort_by="sentAt", sort_order=-1) -> list | None:
        """Retrieve paginated messages for a chat group."""
        cursor = self.chat_messages.find({"chat_id": chat_id}).sort(sort_by, sort_order).skip(skip).limit(limit)
        messages = list(cursor)
        total_messages = self.chat_messages.count_documents({"chat_id": chat_id})
        database_logger.info(f"Fetched {len(messages)} messages for chat '{chat_id}' with skip={skip}, limit={limit}. Total messages: {total_messages}.")
        return messages, total_messages

    def update_message(self, message_id: str, new_content: str) -> bool:
        """Update a message's content."""
        try:
            obj_id = ObjectId(message_id)
        except InvalidId:
            database_logger.warning(f"Invalid ObjectId for message update: {message_id}")
            return False

        result = self.chat_messages.update_one(
            {"_id": obj_id},
            {"$set": {"content": new_content, "editedAt": datetime.now(UTC).replace(tzinfo=None, microsecond=0)}}
        )
        if result.modified_count > 0:
            database_logger.info(f"Updated content of message ID {message_id}.")
            return True
        else:
            database_logger.info(f"No message updated for ID {message_id}.")
            return False

    def delete_message(self, message_id: str) -> bool:
        """Delete a message by ID."""
        try:
            obj_id = ObjectId(message_id)
        except InvalidId:
            database_logger.warning(f"Invalid ObjectId for message deletion: {message_id}")
            return False

        result = self.chat_messages.delete_one({"_id": obj_id})
        if result.deleted_count > 0:
            database_logger.info(f"Deleted message with ID {message_id}.")
            return True
        else:
            database_logger.info(f"No message found to delete with ID {message_id}.")
            return False