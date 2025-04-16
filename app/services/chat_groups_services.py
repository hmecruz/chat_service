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

    def _get_occupants_usernames(self, chat_id: str) -> set[str]:
        occupants_info = self.chat_groups_xmpp.get_room_occupants(chat_id)
        return {o.get("jid").split("@")[0] for o in occupants_info if "jid" in o}

    def create_chat_group(self, group_name: str, users: list[str]) -> dict:
        validate_group_name(group_name)
        validate_users(users)
        
        chat_id = self.chat_groups_dal.create_chat_group(group_name)
        if not chat_id:
            raise ValueError("Chat group not created")

        chat_group = self.chat_groups_dal.get_chat_group(chat_id)
        if not chat_group:
            raise ValueError("Chat group not created")
        if chat_group["groupName"] != group_name:
            raise ValueError("Chat group name not set correctly")
        
        self.xmpp_user_management.ensure_users_register(users)

        success = self.chat_groups_xmpp.create_chat_group(chat_id, users)
        if not success:
            raise ValueError("Failed to create chat group in XMPP")

        occupants = self._get_occupants_usernames(chat_id)
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
        validate_id(chat_id)
        validate_group_name(group_name)

        self.chat_groups_dal.update_chat_group_name(chat_id, group_name)
        chat_group = self.chat_groups_dal.get_chat_group(chat_id)
        if not chat_group:
            raise ValueError(f"Chat group with ID {chat_id} not found")
        if chat_group["groupName"] != group_name:
            raise ValueError("Chat group name not updated")
        
        return {
            "chatId": str(chat_id),
            "groupName": chat_group["groupName"],
        }
    
    def delete_chat_group(self, chat_id: str) -> bool:
        validate_id(chat_id)

        self.chat_groups_xmpp.delete_chat_group(chat_id)

        chat_group = self.chat_groups_dal.get_chat_group(chat_id)
        if not chat_group:
            raise ValueError(f"Chat group with ID {chat_id} not found")

        deleted_count = self.chat_groups_dal.delete_chat_group(chat_id)
        if deleted_count == 1:
            return True

        raise ValueError(f"Chat group with ID {chat_id} not found or already deleted")

    def add_users_to_chat(self, chat_id: str, user_ids: list[str], verify: bool = True) -> list[str]:
        validate_id(chat_id)
        validate_users(user_ids)

        self.xmpp_user_management.ensure_users_register(user_ids)

        success = self.chat_groups_xmpp.add_users_to_room(chat_id, user_ids)
        if not success:
            raise ValueError("Failed to add users to chat group")

        if verify:
            occupants = self._get_occupants_usernames(chat_id)
            missing_users = [user for user in user_ids if user not in occupants]
            if missing_users:
                raise ValueError(f"The following users were not found in the room after addition: {missing_users}")

        return user_ids

    def remove_users_from_chat(self, chat_id: str, user_ids: list[str], verify: bool = True) -> list[str]:
        validate_id(chat_id)
        validate_users(user_ids)

        success = self.chat_groups_xmpp.remove_users_from_room(chat_id, user_ids)
        if not success:
            raise ValueError("Failed to remove one or more users from the chat group")

        if verify:
            occupants = self._get_occupants_usernames(chat_id)
            remaining_users = [user for user in user_ids if user in occupants]
            if remaining_users:
                raise ValueError(f"The following users are still in the room after removal: {remaining_users}")

        return user_ids

    def get_chat_users(self, chat_id: str) -> list[str]:
        validate_id(chat_id)
        return list(self._get_occupants_usernames(chat_id))
        
