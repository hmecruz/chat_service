from bson.objectid import ObjectId
from datetime import datetime
from .database_initializer import ChatServiceDatabase

class ChatGroups:
    def __init__(self, db: ChatServiceDatabase):
        self.chats = db.get_db()["chat_groups"]

    def create_chat_group(self, group_name, users):
        """Creates a new chat group."""
        chat_data = {
            "groupName": group_name,
            "users": users,
            "createdAt": datetime.utcnow(),
        }
        result = self.chats.insert_one(chat_data)
        return str(result.inserted_id)

    def get_chat_group(self, chat_id):
        """Retrieves a chat group by ID."""
        return self.chats.find_one({"_id": ObjectId(chat_id)})

    def update_chat_group(self, chat_id, group_name=None, users=None):
        """Updates a chat group."""
        update_data = {}
        if group_name:
            update_data["groupName"] = group_name
        if users:
            update_data["users"] = users
        if update_data:
            self.chats.update_one({"_id": ObjectId(chat_id)}, {"$set": update_data})

    def delete_chat_group(self, chat_id):
        """Deletes a chat group."""
        self.chats.delete_one({"_id": ObjectId(chat_id)})

    def add_user_to_chat(self, chat_id, user_id):
        """Adds a user to a chat group."""
        self.chats.update_one({"_id": ObjectId(chat_id)}, {"$push": {"users": user_id}})

    def remove_user_from_chat(self, chat_id, user_id):
        """Removes a user from a chat group."""
        self.chats.update_one({"_id": ObjectId(chat_id)}, {"$pull": {"users": user_id}})