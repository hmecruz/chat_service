from base_config import get_env_variable

class Config:
    """Class to store configuration variables."""
    
    MONGO_URI = get_env_variable("MONGO_URI", "mongodb://localhost:27017/")
    MONGO_DB = get_env_variable("MONGO_DB", "chat_service")

    # Dictionary with collections and indexes
    COLLECTIONS = {
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