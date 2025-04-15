from bson.objectid import ObjectId
from datetime import datetime, UTC

from .database_init import ChatServiceDatabase

class ChatGroups:
    def __init__(self, db: ChatServiceDatabase):
        self.chat_groups = db.get_database()["chat_groups"]

    def create_chat_group(self, group_name: str) -> dict:
        """Insert a new chat group into the database."""
        chat_group = {
            "groupName": group_name,
            "createdAt": datetime.now(UTC).replace(tzinfo=None, microsecond=0)
        }
        result = self.chat_groups.insert_one(chat_group)
        return {"_id": str(result.inserted_id)}

    def get_chat_group(self, chat_id: str) -> dict | None:
        """Retrieve a chat group by ID."""
        return self.chat_groups.find_one({"_id": ObjectId(chat_id)})

    def update_chat_group_name(self, chat_id: str, group_name: str) -> bool:
        """Update a chat group's name."""
        result = self.chat_groups.update_one({"_id": ObjectId(chat_id)}, {"$set": {"groupName": group_name}})
        return result.modified_count > 0

    def delete_chat_group(self, chat_id: str) -> int:
        """Delete a chat group."""
        result = self.chat_groups.delete_one({"_id": ObjectId(chat_id)})
        return result.deleted_count