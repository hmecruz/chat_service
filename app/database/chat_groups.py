from bson.objectid import ObjectId
from datetime import datetime
from .database_init import ChatServiceDatabase

class ChatGroups:
    def __init__(self, db: ChatServiceDatabase):
        self.chat_groups = db.get_database()["chat_groups"]

    
    def create_chat_group(self, group_name: str, users: list[str]) -> dict:
        """
        Create a new chat group with the specified name and list of users.

        This method inserts a new document into the chat_groups collection with the provided
        group name and users, along with the current UTC timestamp (with microseconds truncated)
        to indicate the creation time.

        Args:
            group_name (str): The name of the chat group.
            users (list[str]): A list of user IDs to be added to the chat group.

        Returns:
            dict: The created chat group document containing the following keys:
                - "groupName": The name of the group.
                - "users": The list of users in the group.
                - "createdAt": The UTC timestamp when the group was created.
                - "_id": The ObjectId assigned by MongoDB.
        """
        chat_group = {
            "groupName": group_name,
            "users": users,
            "createdAt":  datetime.utcnow().replace(microsecond=0)  # Truncate microseconds
        }
        result = self.chat_groups.insert_one(chat_group)
        chat_group["_id"] = result.inserted_id
        return chat_group
    

    def get_chat_group(self, chat_id: ObjectId) -> dict | None:
        """
        Retrieve a chat group by its unique identifier.

        This method queries the chat_groups collection using the provided ObjectId
        and returns the matching document if found.

        Args:
            chat_id (ObjectId): The unique identifier (_id) of the chat group.

        Returns:
            dict | None: The chat group document if found; otherwise, None.
        """
        group = self.chat_groups.find_one({"_id": ObjectId(chat_id)})
        return group
    
    
    def update_chat_group_name(self, chat_id: ObjectId, group_name: str) -> dict:
        """
        Update a chat group's name.
        
        Args:
            chat_id (ObjectId): The unique identifier of the chat group.
            group_name (str): The new name for the chat group.
        
        Returns:
            dict: A dictionary with the chat_id and the new group name.
        """
        update_data = {}
        if group_name is not None:
            update_data["groupName"] = group_name
        if update_data:
            self.chat_groups.update_one(
                {"_id": ObjectId(chat_id)},
                {"$set": update_data}
            )
        return {"_id": chat_id, "groupName": group_name}
        

    def delete_chat_group(self, chat_id: ObjectId) -> int:
        """
        Delete a chat group by its chat_id.
        Returns the number of documents deleted.
        """
        result = self.chat_groups.delete_one({"_id": ObjectId(chat_id)})
        return result.deleted_count
    

    def add_users_to_chat(self, chat_id: ObjectId, user_ids: list[str]) -> dict:
        """
        Delete a chat group by its unique identifier.

        This method removes the document from the chat_groups collection that matches
        the provided ObjectId.

        Args:
            chat_id (ObjectId): The unique identifier (_id) of the chat group to delete.

        Returns:
            int: The number of documents deleted (should be 1 if the group existed, or 0 if not).
        """
        if user_ids is not []:
            self.chat_groups.update_one(
                {"_id": ObjectId(chat_id)},
                {"$addToSet": {"users": {"$each": user_ids}}}
            )
        updated_group = self.get_chat_group(chat_id)
        return {"_id": chat_id, "users": updated_group.get("users", [])}


    def remove_users_from_chat(self, chat_id: ObjectId, user_ids: list[str]) -> dict:
        """
        Remove multiple users from a chat group's list of users.
        
        Args:
            chat_id (ObjectId): The unique identifier of the chat group.
            user_ids (list[str]): A list of user IDs to remove from the chat group.
        
        Returns:
            dict: A dictionary containing the chat_id and the updated list of users.
        """
        if user_ids is not []:
            self.chat_groups.update_one(
                {"_id": ObjectId(chat_id)},
                {"$pull": {"users": {"$in": user_ids}}}
            )
        updated_group = self.get_chat_group(chat_id)
        return {"_id": chat_id, "users": updated_group.get("users", [])}

    
    def get_chat_groups_for_user(self, user_id: str, page: int = 1, limit: int = 5) -> list:
        """
        Retrieve a paginated list of chat groups that include the specified user.
        Returns a list of chat group documents.
        """
        skip = (page - 1) * limit
        cursor = self.chat_groups.find({"users": user_id}).skip(skip).limit(limit)
        groups = []
        for group in cursor:
            group["chat_id"] = group["_id"]
            groups.append(group)
        return groups