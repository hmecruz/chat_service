from flask import current_app
from flask_socketio import emit

class ChatGroupsEvents:
    def __init__(self):
        self.chat_groups_service = current_app.config['chat_groups_service']

    # -----------------------------------------------------------------------------
    # Event: Create Chat Group
    # Channel: chat/create
    # Publish OperationId: createChatGroup
    # Subscribe OperationId: chatGroupCreated
    # -----------------------------------------------------------------------------
    def handle_create_chat(self, data):
        """
        Expected payload (CreateChatRequest):
          {
            "groupName": "Team Chat",
            "users": ["user1", "user2", "user3"]
          }
        """
        try:
            group_name = data.get('groupName')
            users = data.get('users')
            chat_group = self.chat_groups_service.create_chat_group(group_name, users)
            response = {
                "chatId": str(chat_group["_id"]),
                "groupName": chat_group["groupName"],
                "users": chat_group["users"],
                "createdAt": chat_group["createdAt"]
            }
            emit('chatGroupCreated', response, broadcast=True)
        except Exception as e:
            emit('error', {'error': str(e)})

    # -----------------------------------------------------------------------------
    # Event: Update Chat Group Name
    # Channel: chat/{chatId}/name/update
    # Publish OperationId: updateChatGroupName
    # Subscribe OperationId: chatGroupNameUpdated
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
            emit('chatGroupNameUpdated', response, broadcast=True)
        except Exception as e:
            emit('error', {'error': str(e)})

    # -----------------------------------------------------------------------------
    # Event: Delete Chat Group
    # Channel: chat/delete
    # Publish OperationId: deleteChatGroup
    # Subscribe OperationId: chatGroupDeleted
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
            result = self.chat_groups_service.delete_chat_group(chat_id)
            response = {
                "chatId": chat_id,
                "deleted": result
            }
            emit('chatGroupDeleted', response, broadcast=True)
        except Exception as e:
            emit('error', {'error': str(e)})

    # -----------------------------------------------------------------------------
    # Event: Add Users to Chat Group
    # Channel: chat/{chatId}/users/add
    # Publish OperationId: addUsersToChatGroup
    # Subscribe OperationId: userAddedToChatGroup
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
            emit('usersAddedToChatGroup', response, broadcast=True)
        except Exception as e:
            emit('error', {'error': str(e)})

    # -----------------------------------------------------------------------------
    # Event: Remove Users from Chat Group
    # Channel: chat/{chatId}/users/remove
    # Publish OperationId: removeUsersFromChatGroup
    # Subscribe OperationId: userRemovedFromChatGroup
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
            emit('usersRemovedFromChatGroup', response, broadcast=True)
        except Exception as e:
            emit('error', {'error': str(e)})