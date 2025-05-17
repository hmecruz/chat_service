/**
 * Creates a new chat group.
 * 
 * Server response (on `chatGroupCreated`):
 * {
 *   chatId: string,        // Unique identifier for the new chat group
 *   groupName: string,     // Name of the chat group
 *   users: string[],       // Array of user IDs in the group
 *   createdAt: string      // ISO timestamp of creation
 * }
 */
export function createChatGroup(socket, groupName, users) {
    const payload = { 
        groupName, 
        users 
    };
    socket.emit('chat/create', payload);
}

/**
 * Updates the name of an existing chat group.
 * 
 * Server response (on `chatGroupNameUpdated`):
 * {
 *   chatId: string,        // Identifier of the chat group
 *   newGroupName: string   // The updated group name
 * }
 */
export function updateChatName(socket, chatId, newGroupName) {
    const payload = { 
        chatId, 
        newGroupName 
    };
    socket.emit('chat/name/update', payload);
}

/**
 * Deletes a chat group.
 * 
 * Server response (on `chatGroupDeleted`):
 * {
 *   chatId: string,        // Identifier of the deleted chat group
 *   deleted: boolean       // Whether the deletion succeeded
 * }
 */
export function deleteChat(socket, chatId) {
    const payload = { 
        chatId 
    };
    socket.emit('chat/delete', payload);
}

/**
 * Adds users to an existing chat group.
 * 
 * Server response (on `usersAddedToChatGroup`):
 * {
 *   chatId: string,        // Identifier of the chat group
 *   userIds: string[]      // Array of user IDs that were added
 * }
 */
export function addUsersToChat(socket, chatId, userIds) {
    const payload = { 
        chatId, 
        userIds 
    };
    socket.emit('chat/users/add', payload);
}

/**
 * Removes users from an existing chat group.
 * 
 * Server response (on `usersRemovedFromChatGroup`):
 * {
 *   chatId: string,        // Identifier of the chat group
 *   userIds: string[]      // Array of user IDs that were removed
 * }
 */
export function removeUsersFromChat(socket, chatId, userIds) {
    const payload = { 
        chatId, 
        userIds 
    };
    socket.emit('chat/users/remove', payload);
}
