export function sendMessage(socket, payload) {
    socket.emit('chat/message', payload);
}

export function editMessage(socket, payload) {
    socket.emit('chat/message/edit', payload);
}

export function deleteMessage(socket, payload) {
    socket.emit('chat/message/delete', payload);
}

export function fetchMessageHistory(socket, payload) {
    socket.emit('chat/message/history', payload);
}
