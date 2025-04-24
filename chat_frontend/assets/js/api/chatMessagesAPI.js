export function sendMessage(socket, chatId, senderId, content) {
    const payload = {
        chatId,
        senderId,
        content
    };
    socket.emit('chat/message', payload);
}

export function editMessage(socket, chatId, messageId, newContent) {
    const payload = {
        chatId,
        messageId,
        newContent
    };
    socket.emit('chat/message/edit', payload);
}

export function deleteMessage(socket, chatId, messageId) {
    const payload = {
        chatId,
        messageId
    };
    socket.emit('chat/message/delete', payload);
}

export function fetchMessageHistory(socket, chatId, page = 1, limit = 20) {
    const payload = {
        chatId,
        page,
        limit
    };
    socket.emit('chat/message/history', payload);
}