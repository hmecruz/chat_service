import os
from dotenv import load_dotenv
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
            # Set collections as instance attributes
            self.chat_groups = self.db["chat_groups"]
            self.messages = self.db["messages"]

            # Ensure required collections exist
            self._create_collections_and_indexes()

        except ConnectionFailure as e:
            print(f"Error: Could not connect to MongoDB. {e}")

    def _create_collections_and_indexes(self):
        """Creates collections if they do not exist and sets appropriate indexes."""
        collections = {
            "chat_groups": [
                ("groupName", "text"),  # Full-text search on group names (case-insensitive)
                ("users", 1),  # Index on 'users' for fast lookup (ascending order)
                ("createdAt", -1)  # Sort by creation time (descending order)
            ],
            "messages": [
                ("chat_id", 1),  # Query messages by chat_id (ascending order)
                ("sender_id", 1),  # Search messages by sender (ascending order)
                ("sentAt", -1),  # Sort messages by time (newest first)
                ("content", "text"),  # Full-text search on message content (case-insensitive)
                ("editedAt", -1),  # Sort messages by time (descending order)
                ("deletedAt", -1)  # Sort messages by time (descending order)
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
load_dotenv()
db_instance = ChatServiceDatabase()
print("Connected to DB:", db_instance.get_database().name)