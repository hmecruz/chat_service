from bson.objectid import ObjectId
from bson.errors import InvalidId
from datetime import datetime, UTC

from .database_init import ChatServiceDatabase

from .logger import database_logger


class ChatGroups:
    def __init__(self, db: ChatServiceDatabase):
        # Access the "chat_groups" collection from the database
        self.chat_groups = db.get_database()["chat_groups"]

    def create_chat_group(self, group_name: str) -> dict:
        """Insert a new chat group into the database."""
        chat_group = {
            "groupName": group_name,
            "createdAt": datetime.now(UTC).replace(tzinfo=None, microsecond=0)
        }
        result = self.chat_groups.insert_one(chat_group)
        database_logger.info(f"Created chat group '{group_name}' with ID {result.inserted_id}.")
        return {"_id": str(result.inserted_id)}

    def get_chat_group(self, chat_id: str) -> dict | None:
        """Retrieve a chat group by ID."""
        try:
            obj_id = ObjectId(chat_id)
        except InvalidId:
            database_logger.warning(f"Invalid ObjectId: {chat_id}")
            return None

        group = self.chat_groups.find_one({"_id": obj_id})
        if group:
            database_logger.info(f"Retrieved chat group with ID {chat_id}.")
        else:
            database_logger.info(f"No chat group found with ID {chat_id}.")
        return group
    
    def get_all_chat_group_ids(self) -> list[str]:
        """Retrieve the _id of all chat groups from the database."""
        groups = self.chat_groups.find({}, {"_id": 1}).sort("createdAt", -1)
        group_ids = [str(group["_id"]) for group in groups]
        database_logger.info(f"Retrieved {len(group_ids)} chat group IDs.")
        return group_ids

    def update_chat_group_name(self, chat_id: str, group_name: str) -> bool:
        """Update a chat group's name."""
        try:
            obj_id = ObjectId(chat_id)
        except InvalidId:
            database_logger.warning(f"Invalid ObjectId for update: {chat_id}")
            return False

        result = self.chat_groups.update_one({"_id": obj_id}, {"$set": {"groupName": group_name}})
        if result.modified_count > 0:
            database_logger.info(f"Updated chat group {chat_id} name to '{group_name}'.")
            return True
        else:
            database_logger.info(f"No changes made or group not found for ID {chat_id}.")
            return False

    def delete_chat_group(self, chat_id: str) -> int:
        """Delete a chat group."""
        try:
            obj_id = ObjectId(chat_id)
        except InvalidId:
            database_logger.warning(f"Invalid ObjectId for deletion: {chat_id}")
            return 0

        result = self.chat_groups.delete_one({"_id": obj_id})
        if result.deleted_count > 0:
            database_logger.info(f"Deleted chat group with ID {chat_id}.")
        else:
            database_logger.info(f"No chat group found to delete with ID {chat_id}.")
        return result.deleted_count
    