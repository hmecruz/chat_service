from bson.objectid import ObjectId
from datetime import datetime
from .database_init import ChatServiceDatabase

class ChatMessages:
    def __init__(self, db: ChatServiceDatabase):
        # Access the "messages" collection from the database
        self.messages = db.get_database()["messages"]

    def store_message(self, chat_id: str, sender_id: str, content: str) -> str:
        """
        Store a new message in a chat.
        
        Args:
            chat_id (str): The ID of the chat group.
            sender_id (str): The user ID of the message sender.
            content (str): The content of the message.
            
        Returns:
            str: The inserted message's ID.
        """
        message_data = {
            "chat_id": ObjectId(chat_id),
            "sender_id": sender_id,
            "content": content,
            "sentAt": datetime.utcnow()
        }
        result = self.messages.insert_one(message_data)
        return str(result.inserted_id)

    def get_messages(self, chat_id: str, page: int = 1, limit: int = 20) -> list:
        """
        Retrieve paginated messages for a specific chat group.
        
        Args:
            chat_id (str): The ID of the chat group.
            page (int, optional): The page number. Defaults to 1.
            limit (int, optional): Number of messages per page. Defaults to 20.
            
        Returns:
            list: A list of message documents.
        """
        skip = (page - 1) * limit
        cursor = self.messages.find({"chat_id": ObjectId(chat_id)}) \
                              .sort("sentAt", -1) \
                              .skip(skip) \
                              .limit(limit)
        messages = []
        for message in cursor:
            message["_id"] = str(message["_id"])
            message["chat_id"] = str(message["chat_id"])
            messages.append(message)
        return messages

    def edit_message(self, message_id: str, new_content: str) -> int:
        """
        Edit an existing message's content.
        
        Args:
            message_id (str): The ID of the message to edit.
            new_content (str): The new content for the message.
            
        Returns:
            int: The number of documents modified.
        """
        result = self.messages.update_one(
            {"_id": ObjectId(message_id)},
            {"$set": {"content": new_content, "editedAt": datetime.utcnow()}}
        )
        return result.modified_count

    def delete_message(self, message_id: str) -> int:
        """
        Mark a message as deleted by setting a deletedAt timestamp.
        
        Args:
            message_id (str): The ID of the message to delete.
            
        Returns:
            int: The number of documents modified.
        """
        result = self.messages.update_one(
            {"_id": ObjectId(message_id)},
            {"$set": {"deletedAt": datetime.utcnow()}}
        )
        return result.modified_count
