from app.database.chat_groups import ChatGroups
from app.utils.validators import validate_group_name, validate_users

class ChatGroupsService:
    def __init__(self, chat_groups_dal: ChatGroups):
        self.chat_groups_dal = chat_groups_dal

    def create_chat_group(self, group_name: str, users: list[str]) -> dict:
        """Creates a new chat group after validation."""
        validate_group_name(group_name)
        validate_users(users)

        chat_group = self.chat_groups_dal.create_chat_group(group_name, users)

        if not chat_group or "_id" not in chat_group:
            raise RuntimeError("Failed to create chat group")

        return chat_group


    def update_chat_group_name(self, chat_id: str, group_name: str) -> dict:
        """Validates and updates a chat group's name."""
        validate_group_name(group_name)
        self.chat_groups_dal.update_chat_group_name(chat_id, group_name)

        chat_group = self.chat_groups_dal.get_chat_group(chat_id)
            
        if not chat_group:
            raise ValueError(f"Chat group with ID {chat_id} not found")
        if chat_group["groupName"] != group_name:
            raise ValueError("Chat group name not updated")
        
        return chat_group

    
    def delete_chat_group(self, chat_id: str) -> bool:
        """Deletes a chat group."""
        deleted_count = self.chat_groups_dal.delete_chat_group(chat_id)
        
        if deleted_count == 1:
            return True # Successfully deleted
        else:
            raise ValueError(f"Chat group with ID {chat_id} not found or already deleted")


    def add_users_to_chat(self, chat_id: str, user_ids: list[str]):
        """Validates and adds users to a chat group, verifying success."""
        validate_users(user_ids)

        self.chat_groups_dal.add_users_to_chat(chat_id, user_ids)

        chat_group = self.chat_groups_dal.get_chat_group(chat_id)

        if not chat_group:
            raise ValueError(f"Chat group with ID {chat_id} not found")
        
        if not all(user in chat_group.get("users", []) for user in user_ids):
            raise ValueError("Failed to add some users to the chat group")
        
        return user_ids  # Successfully added users


    def remove_users_from_chat(self, chat_id: str, user_ids: list[str]):
        """Removes users from a chat group."""
        validate_users(user_ids)
        self.chat_groups_dal.remove_users_from_chat(chat_id, user_ids)

        chat_group = self.chat_groups_dal.get_chat_group(chat_id)

        if not chat_group:
            raise ValueError(f"Chat group with ID {chat_id} not found")
        if any(user_id in chat_group["users"] for user_id in user_ids):
            raise ValueError("Failed to remove users from chat group")
        
        return user_ids  # Successfully removed users
    

    def get_chat_groups_for_user(self, user_id: str, page: int = 1, limit: int = 5) -> list:
        """Validates and fetches paginated chat groups."""
        if page < 1 or limit < 1:
            raise ValueError("Page and limit must be greater than zero")

        skip = (page - 1) * limit
        return self.chat_groups_dal.get_chat_groups_for_user(user_id, skip, limit)
