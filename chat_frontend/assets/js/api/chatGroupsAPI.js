export function createChatGroup(socket, groupName, users) {
    const payload = {
        groupName,
        users
    };
    socket.emit('chat/create', payload);
}

export function updateChatName(socket, chatId, newGroupName) {
    const payload = {
        chatId,
        newGroupName
    };
    socket.emit('chat/name/update', payload);
}

export function deleteChat(socket, chatId) {
    const payload = {
        chatId
    };
    socket.emit('chat/delete', payload);
}

export function addUsersToChat(socket, chatId, userIds) {
    const payload = {
        chatId,
        userIds
    };
    socket.emit('chat/users/add', payload);
}

export function removeUsersFromChat(socket, chatId, userIds) {
    const payload = {
        chatId,
        userIds
    };
    socket.emit('chat/users/remove', payload);
}