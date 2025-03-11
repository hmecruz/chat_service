from bson.objectid import ObjectId
from datetime import datetime
from .database_init import ChatServiceDatabase

class ChatMessages:
    def __init__(self, db: ChatServiceDatabase):
        # Access the "messages" collection from the database
        self.messages = db.get_database()["messages"]


    def store_message(self, chat_id: ObjectId, sender_id: str, content: str) -> dict:
        """
        Store a new message in a chat.

        Args:
            chat_id (ObjectId): The ID of the chat group.
            sender_id (str): The user ID of the message sender.
            content (str): The content of the message.

        Returns:
            dict: A dictionary containing the stored message details, including:
                - "_id" (ObjectId): The unique ID of the message.
                - "chat_id" (ObjectId): The chat group ID where the message was sent.
                - "sender_id" (str): The ID of the user who sent the message.
                - "content" (str): The message text.
                - "sentAt" (datetime): The timestamp when the message was sent.
        """
        message_data = {
            "chat_id": ObjectId(chat_id),
            "sender_id": sender_id,
            "content": content,
            "sentAt": datetime.utcnow().replace(microsecond=0)  # Truncate microseconds
        }
        result = self.messages.insert_one(message_data)
        message_data["_id"] = result.inserted_id
        return message_data
    

    def get_message(self, message_id: ObjectId) -> dict | None:
        """
        Retrieve a message by its ID.

        Args:
            message_id (ObjectId): The ID of the message to retrieve.

        Returns:
            dict: A dictionary containing the message details, or None if not found.
        """
        message = self.messages.find_one({"_id": ObjectId(message_id)})
        return message


    def get_messages(self, chat_id: ObjectId, page: int = 1, limit: int = 20) -> list:
        """
        Edit an existing message's content.

        Args:
            message_id (ObjectId): The ID of the message to edit.
            new_content (str): The new content for the message.

        Raises:
            ValueError: If `page` or `limit` is less than 1.    
        
        Returns:
            dict: A dictionary containing the updated message details, including:
                - "_id" (ObjectId): The ID of the edited message.
                - "content" (str): The updated content of the message.
                - "editedAt" (datetime, optional): The timestamp when the message was edited.
        """

        if page < 1 or limit < 1:
            raise ValueError("Page and limit must be greater than zero")

        skip = (page - 1) * limit
        cursor = self.messages.find({"chat_id": ObjectId(chat_id)}) \
                              .sort("sentAt", -1) \
                              .skip(skip) \
                              .limit(limit)
        messages = []
        for message in cursor:
            message["_id"] = message["_id"]
            message["chat_id"] = message["chat_id"]
            messages.append(message)
        return messages
    

    def edit_message(self, message_id: ObjectId, new_content: str) -> dict:
        """
        Edit an existing message's content.
        
        Args:
            message_id (ObjectId): The ID of the message to edit.
            new_content (str): The new content for the message.
            
        Returns:
            dict: A dictionary containing the updated message details, including:
                - "_id" (ObjectId): The ID of the edited message.
                - "content" (str): The updated content of the message.
        """
        if new_content is not None:
            self.messages.update_one(
                {"_id": ObjectId(message_id)},
                {"$set": {"content": new_content, "editedAt": datetime.utcnow().replace(microsecond=0)}}
            )
        return {"_id": message_id, "content": new_content}
    

    def delete_message(self, message_id: ObjectId) -> int:
        """
        Permanent delete a message.
        
        Args:
            message_id (ObjectId): The ID of the message to delete.
            
        Returns:
            int: The number of documents modified.
        """
        result = self.messages.delete_one({"_id": ObjectId(message_id)})
        return result.deleted_count
