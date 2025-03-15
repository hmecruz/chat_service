from flask_socketio import emit
from utils.validators import validate_group_name, validate_users 


# -------------------------------
# Channel: chat/create
# Publish: createChatGroup (CreateChatRequest)
# Subscribe: chatGroupCreated (CreateChatEvent)
# -------------------------------
@socketio.on('createChatGroup')
def handle_create_chat_group(data):
    # groupName: str 
    # users: list[str]
    
    try:
        group_name = validate_group_name(data.get('groupName'))
        users = validate_users(data.get('users'))
    except ValueError as e:
        emit('error', {'error': str(e)})
        return
            
    try:
        response = chat_groups.create_chat_group(group_name, users)
        if response:
            emit('chatGroupCreated', {
                'chatId': str(response['_id']),
                'groupName': response['groupName'],
                'users': response['users'],
                'createdAt': response['createdAt'].isoformat()
            })
    except Exception as e:
        emit('error', {'error': str(e)})
        return
    
    emit('chatGroupCreated', response, broadcast=True)

# -------------------------------
# Channel: chat/{chatId}/user/add
# Publish: addUserToChatGroup (AddUserRequest)
# Subscribe: userAddedToChatGroup (AddUserEvent)
# -------------------------------
@socketio.on('addUserToChatGroup')
def handle_add_user_to_chat_group(data):
    # Expecting data with chatId and userId
    chat_id = data.get('chatId')
    user_id = data.get('userId')
    if not chat_id or not user_id:
        emit('error', {'error': 'Invalid payload for adding user to chat group'})
        return

    added_at = datetime.utcnow().isoformat() + "Z"
    response = {
        'chatId': chat_id,
        'userId': user_id,
        'addedAt': added_at
    }
    emit('userAddedToChatGroup', response, broadcast=True)

# -------------------------------
# Channel: chat/{chatId}/user/remove
# Publish: removeUserFromChatGroup (RemoveUserRequest)
# Subscribe: userRemovedFromChatGroup (RemoveUserEvent)
# -------------------------------
@socketio.on('removeUserFromChatGroup')
def handle_remove_user_from_chat_group(data):
    # Expecting data with chatId and userId
    chat_id = data.get('chatId')
    user_id = data.get('userId')
    if not chat_id or not user_id:
        emit('error', {'error': 'Invalid payload for removing user from chat group'})
        return

    removed_at = datetime.utcnow().isoformat() + "Z"
    response = {
        'chatId': chat_id,
        'userId': user_id,
        'removedAt': removed_at
    }
    emit('userRemovedFromChatGroup', response, broadcast=True)

# -------------------------------
# Channel: chat/delete
# Publish: deleteChatGroup (DeleteChatRequest)
# Subscribe: chatGroupDeleted (DeleteChatEvent)
# -------------------------------
@socketio.on('deleteChatGroup')
def handle_delete_chat_group(data):
    # Expecting data with chatId
    chat_id = data.get('chatId')
    if not chat_id:
        emit('error', {'error': 'Invalid payload for deleting chat group'})
        return

    deleted_at = datetime.utcnow().isoformat() + "Z"
    response = {
        'chatId': chat_id,
        'deletedAt': deleted_at
    }
    emit('chatGroupDeleted', response, broadcast=True)

# -------------------------------
# Channel: user/{userId}/chats
# Publish: requestUserChats (ChatListRequest)
# Subscribe: getUserChats (ChatListEvent)
# -------------------------------
@socketio.on('requestUserChats')
def handle_request_user_chats(data):
    # Expecting data with userId, page, and limit
    user_id = data.get('userId')
    page = data.get('page')
    limit = data.get('limit')
    if not user_id or page is None or limit is None:
        emit('error', {'error': 'Invalid payload for user chats'})
        return

    chats = []
    for i in range(limit):
        chats.append({
            'chatId': generate_id("chat"),
            'groupName': f"Group {i+1}",
            'lastMessage': "Last message excerpt",
            'lastUpdated': datetime.utcnow().isoformat() + "Z"
        })
    response = {
        'userId': user_id,
        'page': page,
        'limit': limit,
        'chats': chats
    }
    emit('getUserChats', response)

if __name__ == '__main__':
    # Run on port 8080 to match the AsyncAPI production server spec.
    socketio.run(app, host='0.0.0.0', port=8080, debug=True)
