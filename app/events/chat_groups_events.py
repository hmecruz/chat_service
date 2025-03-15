from flask import Flask, request
from flask_socketio import SocketIO, emit

# Import our DAL & service layers
from app.database.database_init import ChatServiceDatabase
from app.database.chat_groups import ChatGroups
from app.services.chat_groups_services import ChatGroupsService

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize database, DAL, and service instances
db = ChatServiceDatabase()
chat_groups_dal = ChatGroups(db)
chat_groups_service = ChatGroupsService(chat_groups_dal)

# -----------------------------------------------------------------------------
# Event: Create Chat Group
# Channel: chat/create
# Publish OperationId: createChatGroup
# Subscribe OperationId: chatGroupCreated
# -----------------------------------------------------------------------------
@socketio.on('chat/create')
def handle_create_chat(data):
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
        chat_group = chat_groups_service.create_chat_group(group_name, users)
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
@socketio.on('chat/name/update')
def handle_update_chat_name(data):
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
        updated_group = chat_groups_service.update_chat_group_name(chat_id, new_group_name)
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
@socketio.on('chat/delete')
def handle_delete_chat(data):
    """
    Expected payload (DeleteChatRequest):
      {
        "chatId": "chat123"
      }
    """
    try:
        chat_id = data.get('chatId')
        result = chat_groups_service.delete_chat_group(chat_id)
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
@socketio.on('chat/users/add')
def handle_add_users(data):
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
        added_users = chat_groups_service.add_users_to_chat(chat_id, user_ids)
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
@socketio.on('chat/users/remove')
def handle_remove_users(data):
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
        removed_users = chat_groups_service.remove_users_from_chat(chat_id, user_ids)
        response = {
            "chatId": chat_id,
            "userIds": removed_users
        }
        emit('usersRemovedFromChatGroup', response, broadcast=True)
    except Exception as e:
        emit('error', {'error': str(e)})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080, debug=True)
