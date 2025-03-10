import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


class ChatServiceDatabase:
    def __init__(self):
        # Get database configuration from environment variables
        mongo_uri = os.getenv("MONGO_URI")
        db_name = os.getenv("MONGO_DB")

        if not mongo_uri or not db_name:
            raise ValueError("MONGO_URI and MONGO_DB environment variables must be set")

        try:
            # Initialize MongoDB connection
            self.client = MongoClient(mongo_uri)
            self.db = self.client[db_name]

            # Ensure required collections exist
            self._create_collections_and_indexes()

        except ConnectionFailure as e:
            print(f"Error: Could not connect to MongoDB. {e}")

    def _create_collections_and_indexes(self):
        """Creates collections if they do not exist and sets appropriate indexes."""
        collections = {
            "chat_groups": [
                ("users", 1),  # Index on 'users' for fast lookup (ascending order)
                ("createdAt", -1),  # Sort by creation time (newest first)
                ("groupName", "text")  # Full-text search on group names (case-insensitive)
            ],
            "messages": [
                ("chat_id", 1),  # Query messages by chat_id (ascending order)
                ("sender_id", 1),  # Search messages by sender (ascending order)
                ("sentAt", -1),  # Sort messages by time (newest first)
                ("content", "text"),  # Full-text search on message content (case-insensitive)
                ("editedAt", -1),  # Sort messages by time (newest first)
                ("deletedAt", -1)  # Sort messages by time (newest first)
            ]   
        }

        for collection, indexes in collections.items():
            if collection not in self.db.list_collection_names():
                self.db.create_collection(collection)

            # Ensure indexes for performance
            for field, order in indexes:
                self.db[collection].create_index([(field, order)])

    def get_database(self):
        """Returns the database instance."""
        return self.db
    
    
# Example on how to create and retrieve the database
#db = ChatServiceDatabase()
#db.get_database()
 

    def create_chat_group(self, group_name, users):
        """Create a new chat group with a name and initial user list."""
        chat_group = {
            "groupName": group_name,
            "users": users,
            "createdAt": datetime.utcnow()
        }
        result = self.chat_groups.insert_one(chat_group)
        chat_group["chat_id"] = str(result.inserted_id)

    def get_chat_group(self, chat_id):
        """Retrieve a chat group by its ID."""
        group = self.chat_groups.find_one({"_id": ObjectId(chat_id)})
        if group:
            group["chat_id"] = str(group["_id"])
        return group

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

    def store_message(self, chat_id, sender_id, content):
        """Stores a message."""
        message_data = {
            "chat_id": ObjectId(chat_id),
            "sender_id": sender_id,
            "content": content,
            "sentAt": datetime.utcnow(),
        }
        result = self.messages.insert_one(message_data)
        return str(result.inserted_id)

    def get_messages(self, chat_id, page=1, limit=20):
        """Retrieves messages for a chat with pagination."""
        skip = (page - 1) * limit
        message_list = list(
            self.messages.find({"chat_id": ObjectId(chat_id)})
            .sort("sentAt")
            .skip(skip)
            .limit(limit)
        )
        for message in message_list:
            message["_id"] = str(message["_id"])
            message["chat_id"] = str(message["chat_id"])
        return message_list

    def get_chat_groups_for_user(self, user_id, page=1, limit=10):
        """Retrieve paginated list of chat groups where the user is a member."""
        skip = (page - 1) * limit
        cursor = self.chat_groups.find({"users": user_id}).skip(skip).limit(limit)
        groups = []
        for group in cursor:
            group["chat_id"] = str(group["_id"])
            groups.append(group)
        return groups

    def edit_message(self, message_id, new_content):
        """Edits a message."""
        self.messages.update_one(
            {"_id": ObjectId(message_id)},
            {"$set": {"content": new_content, "editedAt": datetime.utcnow()}},
        )

    def delete_message(self, message_id):
        """Deletes a message."""
        self.messages.update_one(
            {"_id": ObjectId(message_id)},
            {"$set": {"deletedAt": datetime.utcnow()}},
        )
