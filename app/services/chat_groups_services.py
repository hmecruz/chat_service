from flask import current_app
from ..database.chat_groups import ChatGroups
from ..xmpp.user_management_xmpp import UserManagementXMPP
from ..xmpp.chat_groups_xmpp import ChatGroupsXMPP
from ..utils.validators import validate_id, validate_group_name, validate_users

class ChatGroupsService:
    def __init__(self, chat_groups_dal: ChatGroups, xmpp_user_management: UserManagementXMPP):
        self.chat_groups_dal = chat_groups_dal
        self.xmpp_user_management = xmpp_user_management
        self.chat_groups_xmpp = ChatGroupsXMPP()

    def create_chat_group(self, group_name: str, users: list[str]) -> dict:
        """Creates a new chat group after validation."""

        # Validate inputs
        validate_group_name(group_name)
        validate_users(users)
        
        # Create chat group in database
        chat_id = self.chat_groups_dal.create_chat_group(group_name)
        if not chat_id:
            raise ValueError("Chat group not created")

        chat_group = self.chat_groups_dal.get_chat_group(chat_id)
        
        if not chat_group:
            raise ValueError("Chat group not created")
        if chat_group["groupName"] != group_name:
            raise ValueError("Chat group name not set correctly")
        
        # Register users in XMPP if needed
        self.xmpp_user_management.ensure_users_register(users)

        # Create the XMPP chat group (MUC room)
        success = self.chat_groups_xmpp.create_chat_group(chat_id, users)
        if not success:
            raise ValueError("Failed to create chat group in XMPP")

        # Verify users are in the chat group
        occupants_info = self.chat_groups_xmpp.get_room_occupants(chat_id)
        occupants = {occupant.get("jid").split("@")[0] for occupant in occupants_info if "jid" in occupant}
        missing_users = [user for user in users if user not in occupants]

        if missing_users:
            raise ValueError(f"The following users were not added to the XMPP room: {missing_users}")

        return {
            "chatId": str(chat_id),
            "groupName": chat_group["groupName"],
            "users": users,
            "createdAt": chat_group["createdAt"]
        }

    def update_chat_group_name(self, chat_id: str, group_name: str) -> dict:
        """Validates and updates a chat group's name."""
        validate_id(chat_id)
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
        validate_id(chat_id)

        # Delete chat group in XMPP
        self.chat_groups_xmpp.delete_chat_group(chat_id)

        # Delete chat group in database
        chat_group = self.chat_groups_dal.get_chat_group(chat_id)
        if not chat_group:
            raise ValueError(f"Chat group with ID {chat_id} not found")
        
        deleted_count = self.chat_groups_dal.delete_chat_group(chat_id)
        
        if deleted_count == 1:
            return True # Successfully deleted
        raise ValueError(f"Chat group with ID {chat_id} not found or already deleted")

    def add_users_to_chat(self, chat_id: str, user_ids: list[str]):
        """Validates and adds users to a chat group, verifying success."""
        validate_id(chat_id)
        validate_users(user_ids)

        # Ensure users are registered in ejabberd
        self.xmpp_user_management.ensure_users_register(user_ids)

        # Add users to chat group (MUC) in ejabberd
        success = self.chat_groups_xmpp.add_users_to_room(chat_id, user_ids)
        if not success:
            raise ValueError("Failed to add users to chat group")

        # Fetch occupants from the room to verify
        occupants_info = self.chat_groups_xmpp.get_room_occupants(chat_id)
        occupants = {occupant.get("jid").split("@")[0] for occupant in occupants_info if "jid" in occupant}

        # Compare added users with current occupants
        missing_users = [user for user in user_ids if user not in occupants]
        if missing_users:
            raise ValueError(f"The following users were not found in the room after addition: {missing_users}")

        return user_ids

    def remove_users_from_chat(self, chat_id: str, user_ids: list[str]) -> list[str]:
        """Removes users from a chat group via XMPP and verifies successful removal."""
        validate_id(chat_id)
        validate_users(user_ids)

        # Attempt to remove users from the room
        success = self.chat_groups_xmpp.remove_users_from_room(chat_id, user_ids)
        if not success:
            raise ValueError("Failed to remove one or more users from the chat group")

        # Fetch current occupants to verify removal
        occupants_info = self.chat_groups_xmpp.get_room_occupants(chat_id)
        occupants = {occupant.get("jid").split("@")[0] for occupant in occupants_info if "jid" in occupant}

        # Check if any users are still present
        remaining_users = [user for user in user_ids if user in occupants]
        if remaining_users:
            raise ValueError(f"The following users are still in the room after removal: {remaining_users}")

        return user_ids  # Successfully removed users
