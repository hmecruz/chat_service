from flask import current_app
from ..database.chat_groups import ChatGroups
from ..xmpp.user_management_xmpp import UserManagementXMPP
from ..xmpp.chat_groups_xmpp import ChatGroupsXMPP
from ..utils.validators import validate_id, validate_group_name, validate_users

from .logger import services_logger

class ChatGroupsService:
    def __init__(self, chat_groups_dal: ChatGroups, xmpp_user_management: UserManagementXMPP):
        self.chat_groups_dal = chat_groups_dal
        self.xmpp_user_management = xmpp_user_management
        self.chat_groups_xmpp = ChatGroupsXMPP()

    def _get_occupants_usernames(self, chat_id: str) -> set[str]:
        try:
            services_logger.info(f"Getting occupants for chat group with ID: {chat_id}")
            occupants_info = self.chat_groups_xmpp.get_room_affiliated_usernames(chat_id)
            occupants = {o.get("jid").split("@")[0] for o in occupants_info if "jid" in o}
            services_logger.info(f"Found occupants: {occupants}")
            return occupants
        except Exception as e:
            services_logger.error(f"Error getting occupants for chat group ID {chat_id}: {e}")
            raise

    def create_chat_group(self, group_name: str, users: list[str]) -> dict:
        try:
            services_logger.info(f"Creating chat group '{group_name}' with users: {users}")
            validate_group_name(group_name)
            validate_users(users)

            chat_id = self.chat_groups_dal.create_chat_group(group_name).get("_id")
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

            services_logger.info(f"Chat group '{group_name}' created successfully with ID: {chat_id}")
            return {
                "chatId": str(chat_id),
                "groupName": chat_group["groupName"],
                "users": users,
                "createdAt": chat_group["createdAt"]
            }
        except Exception as e:
            services_logger.error(f"Error creating chat group '{group_name}': {e}")
            raise

    def update_chat_group_name(self, chat_id: str, group_name: str) -> dict:
        try:
            services_logger.info(f"Updating chat group with ID {chat_id} to new name '{group_name}'")
            validate_id(chat_id)
            validate_group_name(group_name)

            self.chat_groups_dal.update_chat_group_name(chat_id, group_name)
            chat_group = self.chat_groups_dal.get_chat_group(chat_id)
            if not chat_group:
                raise ValueError(f"Chat group with ID {chat_id} not found")
            if chat_group["groupName"] != group_name:
                raise ValueError("Chat group name not updated")

            services_logger.info(f"Chat group with ID {chat_id} successfully updated to '{group_name}'")
            return {
                "chatId": str(chat_id),
                "groupName": chat_group["groupName"],
                "users": chat_group.get("users"),
            }
        except Exception as e:
            services_logger.error(f"Error updating chat group with ID {chat_id}: {e}")
            raise

    def delete_chat_group(self, chat_id: str) -> bool:
        try:
            services_logger.info(f"Deleting chat group with ID {chat_id}")
            validate_id(chat_id)

            self.chat_groups_xmpp.delete_chat_group(chat_id)

            chat_group = self.chat_groups_dal.get_chat_group(chat_id)
            if not chat_group:
                raise ValueError(f"Chat group with ID {chat_id} not found")

            deleted_count = self.chat_groups_dal.delete_chat_group(chat_id)
            if deleted_count == 1:
                services_logger.info(f"Chat group with ID {chat_id} deleted successfully")
                return True

            raise ValueError(f"Chat group with ID {chat_id} not found or already deleted")
        except Exception as e:
            services_logger.error(f"Error deleting chat group with ID {chat_id}: {e}")
            raise

    def add_users_to_chat(self, chat_id: str, user_ids: list[str], verify: bool = True) -> list[str]:
        try:
            services_logger.info(f"Adding users {user_ids} to chat group with ID {chat_id}")
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

            services_logger.info(f"Users {user_ids} added to chat group with ID {chat_id}")
            return user_ids
        except Exception as e:
            services_logger.error(f"Error adding users to chat group with ID {chat_id}: {e}")
            raise

    def remove_users_from_chat(self, chat_id: str, user_ids: list[str], verify: bool = True) -> list[str]:
        try:
            services_logger.info(f"Removing users {user_ids} from chat group with ID {chat_id}")
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

            services_logger.info(f"Users {user_ids} removed from chat group with ID {chat_id}")
            return user_ids
        except Exception as e:
            services_logger.error(f"Error removing users from chat group with ID {chat_id}: {e}")
            raise

    def get_chat_users(self, chat_id: str) -> list[str]:
        try:
            services_logger.info(f"Getting users for chat group with ID {chat_id}")
            validate_id(chat_id)
            users = list(self._get_occupants_usernames(chat_id))
            services_logger.info(f"Found users in chat group {chat_id}: {users}")
            return users
        except Exception as e:
            services_logger.error(f"Error getting users for chat group with ID {chat_id}: {e}")
            raise
