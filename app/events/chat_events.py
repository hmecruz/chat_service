from flask import Flask
from flask_socketio import SocketIO, emit
from datetime import datetime
import uuid
from datetime import datetime

from app.main import chat_groups
from app.main import chat_messages

from utils.utils import convert_id_to_chat_id

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# -------------------------------
# Channel: chat/create
# Publish: createChatGroup (CreateChatRequest)
# Subscribe: chatGroupCreated (CreateChatEvent)
# -------------------------------
@socketio.on('createChatGroup')
def handle_create_chat_group(data):
    # Expecting data with keys: groupName: str and users: list[str]
    
    try:
        group_name = data.get('groupName')
        if not group_name:
            raise Exception("Missing groupName")
        elif not isinstance(group_name, str):
            raise Exception("Invalid groupName type")
        elif len(group_name) > 25:
            raise Exception("groupName exceeds 50 characters")
        
        users = data.get('users')
        if not users:
            raise Exception("Missing users")
        elif not isinstance(users, list):
            raise Exception("Invalid users type")
        elif len(users) < 2:
            raise Exception("At least 2 users required")
        elif len(users) > 20:
            raise Exception("Maximum 10 users allowed")
        for user in users:
            if not isinstance(user, str):
                raise Exception("Invalid user type")
            elif len(user) > 25:
                raise Exception("User ID exceeds 25 characters")
    except Exception as e:
        emit('error', {'error': 'Invalid payload for creating chat group'})
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
# Channel: chat/{chatId}/message
# Publish: sendMessage (SendMessageRequest)
# Subscribe: receiveMessage (SendMessageEvent)
# -------------------------------
@socketio.on('sendMessage')
def handle_send_message(data):
    # Expecting data with chatId, senderId, and content
    chat_id = data.get('chatId')
    sender_id = data.get('senderId')
    content = data.get('content')
    if not chat_id or not sender_id or not content:
        emit('error', {'error': 'Invalid payload for sending message'})
        return

    sent_at = datetime.utcnow().isoformat() + "Z"
    message_id = generate_id("msg")
    # For simplicity, we assume a single message (pagination placeholders added)
    response = {
        'chatId': chat_id,
        'page': 1,       # Placeholder for pagination
        'limit': 20,     # Placeholder for pagination
        'total': 1,      # Placeholder total count
        'messages': [{
            'messageId': message_id,
            'senderId': sender_id,
            'content': content,
            'sentAt': sent_at
        }]
    }
    emit('receiveMessage', response, broadcast=True)

# -------------------------------
# Channel: chat/{chatId}/message/edit
# Publish: editMessage (EditMessageRequest)
# Subscribe: messageEdited (EditMessageEvent)
# -------------------------------
@socketio.on('editMessage')
def handle_edit_message(data):
    # Expecting data with chatId, messageId, and newContent
    chat_id = data.get('chatId')
    message_id = data.get('messageId')
    new_content = data.get('newContent')
    if not chat_id or not message_id or not new_content:
        emit('error', {'error': 'Invalid payload for editing message'})
        return

    edited_at = datetime.utcnow().isoformat() + "Z"
    response = {
        'chatId': chat_id,
        'messageId': message_id,
        'newContent': new_content,
        'editedAt': edited_at
    }
    emit('messageEdited', response, broadcast=True)

# -------------------------------
# Channel: chat/{chatId}/message/delete
# Publish: deleteMessage (DeleteMessageRequest)
# Subscribe: messageDeleted (DeleteMessageEvent)
# -------------------------------
@socketio.on('deleteMessage')
def handle_delete_message(data):
    # Expecting data with chatId and messageId
    chat_id = data.get('chatId')
    message_id = data.get('messageId')
    if not chat_id or not message_id:
        emit('error', {'error': 'Invalid payload for deleting message'})
        return

    deleted_at = datetime.utcnow().isoformat() + "Z"
    response = {
        'chatId': chat_id,
        'messageId': message_id,
        'deletedAt': deleted_at
    }
    emit('messageDeleted', response, broadcast=True)

# -------------------------------
# Channel: chat/{chatId}/message/history
# Publish: requestMessageHistory (MessageHistoryRequest)
# (No subscribe event defined; using 'receiveMessageHistory' for response)
# -------------------------------
@socketio.on('requestMessageHistory')
def handle_request_message_history(data):
    # Expecting data with chatId, page, and limit
    chat_id = data.get('chatId')
    page = data.get('page')
    limit = data.get('limit')
    if not chat_id or page is None or limit is None:
        emit('error', {'error': 'Invalid payload for message history'})
        return

    total_messages = 50  # Placeholder total
    messages = []
    for i in range(limit):
        messages.append({
            'messageId': generate_id("msg"),
            'senderId': "user1",  # Dummy sender
            'content': f"Message {i+1}",
            'sentAt': datetime.utcnow().isoformat() + "Z"
        })
    response = {
        'chatId': chat_id,
        'page': page,
        'limit': limit,
        'total': total_messages,
        'messages': messages
    }
    # Emit the message history back to the requesting client
    emit('receiveMessageHistory', response)

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
