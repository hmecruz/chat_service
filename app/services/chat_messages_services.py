from ..utils.validators import validate_id, validate_message_content
from ..xmpp.chat_messages_xmpp import ChatMessagesXMPP
from ..database.chat_messages import ChatMessages

from .logger import services_logger

class ChatMessagesService:
    def __init__(self, chat_messages_dal: ChatMessages):
        """Business logic layer for chat messages."""
        self.chat_messages_dal = chat_messages_dal
        self.chat_messages_xmpp = ChatMessagesXMPP()

    def send_message(self, chat_id: str, sender_id: str, content: str) -> dict:
        services_logger.info(f"Attempting to send message from {sender_id} to {chat_id}")

        try:
            validate_id(chat_id)
            validate_id(sender_id)
            validate_message_content(content)
            services_logger.debug(f"Validated chat_id: {chat_id}, sender_id: {sender_id}, content length: {len(content)}")

            success = self.chat_messages_xmpp.send_message(
                user_id=sender_id,
                to_id=chat_id,
                message_type="groupchat",
                subject="",
                body=content
            )
            if not success:
                raise RuntimeError("Failed to send message via XMPP")
            services_logger.info(f"Message sent successfully via XMPP to {chat_id}")

            message_id = self.chat_messages_dal.insert_message(chat_id, sender_id, content)
            if not message_id:
                raise RuntimeError("Failed to store message")
            services_logger.info(f"Message stored in database with ID: {message_id}")

            message = self.chat_messages_dal.fetch_message(message_id)
            if not message:
                raise RuntimeError("Failed to retrieve stored message")
            services_logger.info(f"Message retrieved from database: {message_id}")

            if str(message["chat_id"]) != chat_id:
                raise RuntimeError("Chat ID mismatch in stored message")
            if message["sender_id"] != sender_id:
                raise RuntimeError("Sender ID mismatch in stored message")
            if message["content"] != content:
                raise RuntimeError("Content mismatch in stored message")

            services_logger.info(f"Message validated successfully with content: {content}")
            return message
        except Exception as e:
            services_logger.error(f"Error in send_message: {e}")
            raise

    def get_message(self, message_id: str) -> dict:
        services_logger.info(f"Fetching message with ID: {message_id}")

        try:
            validate_id(message_id)
            message = self.chat_messages_dal.fetch_message(message_id)
            if not message:
                raise ValueError(f"Message with ID {message_id} not found")
            services_logger.info(f"Message retrieved successfully: {message_id}")
            return message
        except Exception as e:
            services_logger.error(f"Error in get_message: {e}")
            raise

    def get_messages(self, chat_id: str, page: int = 1, limit: int = 20) -> list[dict]:
        services_logger.info(f"Fetching messages for chat_id: {chat_id}, page: {page}, limit: {limit}")

        try:
            validate_id(chat_id)
            if page < 1 or limit < 1:
                raise ValueError("Page and limit must be greater than zero")
            skip = (page - 1) * limit
            messages = self.chat_messages_dal.fetch_messages(chat_id, skip, limit)
            services_logger.info(f"Fetched {len(messages)} messages for chat_id: {chat_id}")
            return messages
        except Exception as e:
            services_logger.error(f"Error in get_messages: {e}")
            raise

    def edit_message(self, chat_id: str, message_id: str, new_content: str) -> dict:
        services_logger.info(f"Editing message with ID: {message_id} for chat_id: {chat_id}")

        try:
            validate_id(chat_id)
            validate_id(message_id)
            validate_message_content(new_content)

            updated = self.chat_messages_dal.update_message(message_id, new_content)
            if not updated:
                raise RuntimeError("Failed to update message")
            services_logger.info(f"Message with ID: {message_id} updated successfully")

            updated_message = self.chat_messages_dal.fetch_message(message_id)
            if not updated_message:
                raise RuntimeError("Failed to retrieve updated message")

            if updated_message["chat_id"] != chat_id:
                raise RuntimeError("Chat ID mismatch in updated message")
            if updated_message["content"] != new_content:
                raise RuntimeError("Content mismatch in updated message")
            if updated_message.get("editedAt") is None:
                raise RuntimeError("Missing editedAt timestamp in updated message")

            services_logger.info(f"Message edited successfully: {message_id}")
            return updated_message
        except Exception as e:
            services_logger.error(f"Error in edit_message: {e}")
            raise

    def delete_message(self, chat_id: str, message_id: str) -> bool:
        services_logger.info(f"Attempting to delete message with ID: {message_id} for chat_id: {chat_id}")

        try:
            validate_id(chat_id)
            validate_id(message_id)

            deleted = self.chat_messages_dal.delete_message(message_id)
            if not deleted:
                raise ValueError(f"Message with ID {message_id} not found or already deleted")

            # Confirm deletion
            message = self.chat_messages_dal.fetch_message(message_id)
            if message is not None:
                raise RuntimeError("Message still exists after deletion")

            services_logger.info(f"Message with ID {message_id} deleted successfully")
            return True
        except Exception as e:
            services_logger.error(f"Error in delete_message: {e}")
            raise
