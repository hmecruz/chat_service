from bson.objectid import ObjectId
from datetime import datetime, UTC
from .database_init import ChatServiceDatabase

class ChatGroups:
    def __init__(self, db: ChatServiceDatabase):
        self.chat_groups = db.get_database()["chat_groups"]


    def create_chat_group(self, group_name: str, users: list[str]) -> dict:
        """Insert a new chat group into the database."""
        chat_group = {
            "groupName": group_name,
            "users": users,
            "createdAt": datetime.now(UTC).replace(tzinfo=None, microsecond=0)
        }
        result = self.chat_groups.insert_one(chat_group)
        return result.inserted_id
       

    def get_chat_group(self, chat_id: str) -> dict | None:
        """Retrieve a chat group by ID."""
        return self.chat_groups.find_one({"_id": ObjectId(chat_id)})


    def update_chat_group_name(self, chat_id: str, group_name: str):
        """Update a chat group's name."""
        result = self.chat_groups.update_one({"_id": ObjectId(chat_id)}, {"$set": {"groupName": group_name}})
        return result.modified_count > 0
    

    def delete_chat_group(self, chat_id: str) -> int:
        """Delete a chat group."""
        result = self.chat_groups.delete_one({"_id": ObjectId(chat_id)})
        return result.deleted_count


    def add_users_to_chat(self, chat_id: str, user_ids: list[str]) -> None:
        """Add users to a chat group."""
        self.chat_groups.update_one({"_id": ObjectId(chat_id)}, {"$addToSet": {"users": {"$each": user_ids}}})
        

    def remove_users_from_chat(self, chat_id: str, user_ids: list[str]) -> None:
        """Remove users from a chat group."""
        self.chat_groups.update_one({"_id": ObjectId(chat_id)}, {"$pull": {"users": {"$in": user_ids}}})


    def get_chat_groups_for_user(self, user_id: str, skip: int, limit: int) -> list:
        """Retrieve paginated chat groups for a user."""
        cursor = self.chat_groups.find({"users": user_id}).skip(skip).limit(limit)
        return list(cursor)
