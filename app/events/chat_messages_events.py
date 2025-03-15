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
