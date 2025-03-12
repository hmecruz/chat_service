from config.database_config import DatabaseConfig
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


class ChatServiceDatabase:
    def __init__(self):
        """Initialize MongoDB connection and setup collections."""
        try:
            self.client = MongoClient(DatabaseConfig.MONGO_URI)
            self.db = self.client[DatabaseConfig.MONGO_DB]
            self.chat_groups = self.db["chat_groups"]
            self.messages = self.db["chat_messages"]

            # Create collections and indexes
            self._create_collections_and_indexes()

        except ConnectionFailure as e:
            print(f"Error: Could not connect to MongoDB. {e}")

    def _create_collections_and_indexes(self):
        """Ensure collections exist and create necessary indexes."""
        for collection, indexes in DatabaseConfig.COLLECTIONS.items():
            if collection not in self.db.list_collection_names():
                self.db.create_collection(collection)

            # Create indexes
            for field, order in indexes:
                self.db[collection].create_index([(field, order)], background=True)

    def get_database(self):
        """Returns the database instance."""
        return self.db