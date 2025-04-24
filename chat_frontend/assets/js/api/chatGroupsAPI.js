export function createChatGroup(socket, groupName, users) {
    const payload = {
        groupName,
        users
    };
    socket.emit('chat/create', payload);
}

export function updateChatName(socket, payload) {
    socket.emit('chat/name/update', payload);
}

export function deleteChat(socket, payload) {
    socket.emit('chat/delete', payload);
}

export function addUsersToChat(socket, payload) {
    socket.emit('chat/users/add', payload);
}

export function removeUsersFromChat(socket, payload) {
    socket.emit('chat/users/remove', payload);
}