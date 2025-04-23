from flask import current_app, has_request_context, request
from flask_socketio import emit
from .logger import events_logger  # Assuming logger is set up in this file

class ChatGroupsEvents:
    def __init__(self):
        self.chat_groups_service = current_app.config['chat_groups_service']

    def _emit_success(self, event_name, response, target_user_ids=None):
        """
        Emit success to specific user rooms, or fallback to broadcast (e.g., in tests).
        """
        if target_user_ids:
            for user_id in target_user_ids:
                emit(event_name, response, room=user_id)
        elif has_request_context() and hasattr(request, 'sid'):
            emit(event_name, response, room=request.sid)
        else:
            emit(event_name, response, broadcast=True)

    def _emit_error(self, error_type, message):
        if has_request_context() and hasattr(request, 'sid'):
            emit('error', {
                "type": error_type,
                "message": message
            }, room=request.sid)
        else:
            emit('error', {
                "type": error_type,
                "message": message
            }, broadcast=True)

    # -------------------------------------------------------------------------
    # Event: Create Chat Group
    # Channel: chat/create
    # -------------------------------------------------------------------------
    def handle_create_chat(self, data):
        """
        Expected payload (CreateChatRequest):
          {
            "groupName": "Team Chat",
            "users": ["owner", "user1", "user2"]
          }
        """
        try:
            group_name = data.get('groupName')
            users = data.get('users')

            if not group_name or not users:
                raise ValueError("Invalid request: groupName and users are required fields")
            if len(users) < 2:
                raise ValueError("Invalid request: chat group must have at least 2 users")

            # Log the request to create a chat group
            events_logger.info(f"Creating chat group: {group_name} for users: {users}")

            chat_group = self.chat_groups_service.create_chat_group(group_name, users)
            chat_id = str(chat_group["chatId"])

            response = {
                "chatId": chat_id,
                "groupName": chat_group["groupName"],
                "users": chat_group["users"],
                "createdAt": chat_group["createdAt"].isoformat()
            }

            # Log successful creation of chat group
            events_logger.info(f"Chat group created: {chat_id} ({group_name})")
            self._emit_success('chatGroupCreated', response, target_user_ids=chat_group["users"])

        except Exception as e:
            # Log error during chat group creation
            events_logger.error(f"Error creating chat group: {str(e)}")
            self._emit_error("creation_error", str(e))

    # -------------------------------------------------------------------------
    # Event: Update Chat Group Name
    # Channel: chat/{chatId}/name/update
    # -------------------------------------------------------------------------
    def handle_update_chat_name(self, data):
        """
        Expected payload (UpdateChatNameRequest):
          {
            "chatId": "chat123",
            "newGroupName": "New Team Chat Name"
          }
        """
        try:
            chat_id = data.get('chatId')
            new_group_name = data.get('newGroupName')

            # Log the request to update the chat group name
            events_logger.info(f"Updating chat group name: {chat_id} to {new_group_name}")

            updated_group = self.chat_groups_service.update_chat_group_name(chat_id, new_group_name)

            response = {
                "chatId": chat_id,
                "newGroupName": updated_group["groupName"]
            }

            # Log successful update
            events_logger.info(f"Chat group name updated: {chat_id} to {new_group_name}")

            self._emit_success('chatGroupNameUpdated', response, target_user_ids=updated_group["users"])

        except Exception as e:
            # Log error during chat group name update
            events_logger.error(f"Error updating chat group name: {str(e)}")
            self._emit_error("update_error", str(e))

    # -------------------------------------------------------------------------
    # Event: Delete Chat Group
    # Channel: chat/delete
    # -------------------------------------------------------------------------
    def handle_delete_chat(self, data):
        """
        Expected payload (DeleteChatRequest):
          {
            "chatId": "chat123"
          }
        """
        try:
            chat_id = data.get('chatId')

            # Log the request to delete the chat group
            events_logger.info(f"Deleting chat group: {chat_id}")

            result, affected_users = self.chat_groups_service.delete_chat_group(chat_id)

            response = {
                "chatId": chat_id,
                "deleted": result
            }

            # Log successful deletion
            if result:
                events_logger.info(f"Chat group deleted: {chat_id}")
            else:
                events_logger.warning(f"Failed to delete chat group: {chat_id}")

            self._emit_success('chatGroupDeleted', response, target_user_ids=affected_users)

        except Exception as e:
            # Log error during chat group deletion
            events_logger.error(f"Error deleting chat group: {str(e)}")
            self._emit_error("deletion_error", str(e))

    # -------------------------------------------------------------------------
    # Event: Add Users to Chat Group
    # Channel: chat/{chatId}/users/add
    # -------------------------------------------------------------------------
    def handle_add_users(self, data):
        """
        Expected payload (AddUsersRequest):
          {
            "chatId": "chat123",
            "userIds": ["user4", "user5", "user6"]
          }
        """
        try:
            chat_id = data.get('chatId')
            user_ids = data.get('userIds')

            # Log the request to add users to chat
            events_logger.info(f"Adding users {user_ids} to chat group: {chat_id}")

            added_users, target_user_ids = self.chat_groups_service.add_users_to_chat(chat_id, user_ids)

            response = {
                "chatId": chat_id,
                "userIds": added_users
            }

            # Log successful user addition
            events_logger.info(f"Users added to chat group: {chat_id} - {added_users}")

            self._emit_success('usersAddedToChatGroup', response, target_user_ids)

        except Exception as e:
            # Log error during user addition
            events_logger.error(f"Error adding users to chat group: {str(e)}")
            self._emit_error("add_users_error", str(e))

    # -------------------------------------------------------------------------
    # Event: Remove Users from Chat Group
    # Channel: chat/{chatId}/users/remove
    # -------------------------------------------------------------------------
    def handle_remove_users(self, data):
        """
        Expected payload (RemoveUsersRequest):
          {
            "chatId": "chat123",
            "userIds": ["user4", "user5"]
          }
        """
        try:
            chat_id = data.get('chatId')
            user_ids = data.get('userIds')

            # Log the request to remove users from chat
            events_logger.info(f"Removing users {user_ids} from chat group: {chat_id}")

            removed_users, target_user_ids = self.chat_groups_service.remove_users_from_chat(chat_id, user_ids)

            response = {
                "chatId": chat_id,
                "userIds": removed_users
            }

            # Log successful user removal
            events_logger.info(f"Users removed from chat group: {chat_id} - {removed_users}")

            self._emit_success('usersRemovedFromChatGroup', response, target_user_ids)

        except Exception as e:
            # Log error during user removal
            events_logger.error(f"Error removing users from chat group: {str(e)}")
            self._emit_error("remove_users_error", str(e))
