from bson.objectid import ObjectId
from datetime import datetime
from .database_initializer import ChatServiceDatabase

class ChatGroups:
    def __init__(self, db: ChatServiceDatabase):
        self.chat_groups = db.get_db()["chat_groups"]
    
    def create_chat_group(self, group_name: str, users: list) -> dict:
        """
        Create a new chat group with a given name and initial list of users.
        Returns the created chat group document including the generated chat_id.
        """
        chat_group = {
            "groupName": group_name,
            "users": users,
            "createdAt": datetime.utcnow()
        }
        result = self.chat_groups.insert_one(chat_group)
        chat_group["chat_id"] = str(result.inserted_id)
        return chat_group

    def get_chat_group(self, chat_id: str) -> dict:
        """
        Retrieve a chat group by its chat_id.
        Returns the chat group document if found, otherwise None.
        """
        group = self.chat_groups.find_one({"_id": ObjectId(chat_id)})
        if group:
            group["chat_id"] = str(group["_id"])
        return group

    def update_chat_group(self, chat_id: str, group_name: str = None, users: list = None) -> int:
        """
        Update a chat group's details. You can update the group name and/or the list of users.
        Returns the number of documents modified.
        """
        update_data = {}
        if group_name is not None:
            update_data["groupName"] = group_name
        if users is not None:
            update_data["users"] = users
        if update_data:
            result = self.chat_groups.update_one(
                {"_id": ObjectId(chat_id)},
                {"$set": update_data}
            )
            return result.modified_count
        return 0

    def delete_chat_group(self, chat_id: str) -> int:
        """
        Delete a chat group by its chat_id.
        Returns the number of documents deleted.
        """
        result = self.chat_groups.delete_one({"_id": ObjectId(chat_id)})
        return result.deleted_count

    def add_user_to_chat(self, chat_id: str, user_id: str) -> int:
        """
        Add a user to a chat group's list of users.
        Uses $addToSet to ensure the user is not added more than once.
        Returns the number of documents modified.
        """
        result = self.chat_groups.update_one(
            {"_id": ObjectId(chat_id)},
            {"$addToSet": {"users": user_id}}
        )
        return result.modified_count

    def remove_user_from_chat(self, chat_id: str, user_id: str) -> int:
        """
        Remove a user from a chat group's list of users.
        Returns the number of documents modified.
        """
        result = self.chat_groups.update_one(
            {"_id": ObjectId(chat_id)},
            {"$pull": {"users": user_id}}
        )
        return result.modified_count

    def get_chat_groups_for_user(self, user_id: str, page: int = 1, limit: int = 10) -> list:
        """
        Retrieve a paginated list of chat groups that include the specified user.
        Returns a list of chat group documents.
        """
        skip = (page - 1) * limit
        cursor = self.chat_groups.find({"users": user_id}).skip(skip).limit(limit)
        groups = []
        for group in cursor:
            group["chat_id"] = str(group["_id"])
            groups.append(group)
        return groups