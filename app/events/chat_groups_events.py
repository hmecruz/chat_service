from flask import current_app, has_request_context, request
from flask_socketio import emit


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

    # -----------------------------------------------------------------------------
    # Event: Create Chat Group
    # Channel: chat/create
    # -----------------------------------------------------------------------------
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

            chat_group = self.chat_groups_service.create_chat_group(group_name, users)
            chat_id = str(chat_group["_id"])

            response = {
                "chatId": chat_id,
                "groupName": chat_group["groupName"],
                "users": chat_group["users"],
                "createdAt": chat_group["createdAt"]
            }
            self._emit_success('chatGroupCreated', response, target_user_ids=chat_group["users"])
        except Exception as e:
            self._emit_error("creation_error", str(e))

    # -----------------------------------------------------------------------------
    # Event: Update Chat Group Name
    # Channel: chat/{chatId}/name/update
    # -----------------------------------------------------------------------------
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

            updated_group = self.chat_groups_service.update_chat_group_name(chat_id, new_group_name)

            response = {
                "chatId": chat_id,
                "newGroupName": updated_group["groupName"]
            }
            self._emit_success('chatGroupNameUpdated', response, target_user_ids=updated_group["users"])
        except Exception as e:
            self._emit_error("update_error", str(e))

    # -----------------------------------------------------------------------------
    # Event: Delete Chat Group
    # Channel: chat/delete
    # -----------------------------------------------------------------------------
    def handle_delete_chat(self, data):
        """
        Expected payload (DeleteChatRequest):
          {
            "chatId": "chat123"
          }
        """
        try:
            chat_id = data.get('chatId')
            result, affected_users = self.chat_groups_service.delete_chat_group(chat_id)

            response = {
                "chatId": chat_id,
                "deleted": result
            }
            self._emit_success('chatGroupDeleted', response, target_user_ids=affected_users)
        except Exception as e:
            self._emit_error("deletion_error", str(e))

    # -----------------------------------------------------------------------------
    # Event: Add Users to Chat Group
    # Channel: chat/{chatId}/users/add
    # -----------------------------------------------------------------------------
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
            added_users = self.chat_groups_service.add_users_to_chat(chat_id, user_ids)

            response = {
                "chatId": chat_id,
                "userIds": added_users
            }
            self._emit_success('usersAddedToChatGroup', response, target_user_ids=added_users)
        except Exception as e:
            self._emit_error("add_users_error", str(e))

    # -----------------------------------------------------------------------------
    # Event: Remove Users from Chat Group
    # Channel: chat/{chatId}/users/remove
    # -----------------------------------------------------------------------------
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
            removed_users = self.chat_groups_service.remove_users_from_chat(chat_id, user_ids)

            response = {
                "chatId": chat_id,
                "userIds": removed_users
            }
            self._emit_success('usersRemovedFromChatGroup', response, target_user_ids=removed_users)
        except Exception as e:
            self._emit_error("remove_users_error", str(e))
