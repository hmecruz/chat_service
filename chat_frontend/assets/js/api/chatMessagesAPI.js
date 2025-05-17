/**
 * Sends a new message to a chat group.
 * 
 * Server response (on `receiveMessage`):
 * {
 *   chatId: string,        // Identifier of the chat group
 *   page: number,          // Page number (for pagination)
 *   limit: number,         // Messages per page
 *   total: number,         // Total number of messages available
 *   messages: [            // Array of message objects
 *     {
 *       messageId: string,
 *       senderId: string,
 *       content: string,
 *       sentAt: string     // ISO timestamp
 *     },
 *     …
 *   ]
 * }
 */
export function sendMessage(socket, chatId, senderId, content) {
    const payload = { 
        chatId, 
        senderId, 
        content };
    socket.emit('chat/message', payload);
}

/**
 * Edits an existing message in a chat group.
 * 
 * Server response (on `messageEdited`):
 * {
 *   chatId: string,        // Identifier of the chat group
 *   messageId: string,     // Identifier of the edited message
 *   newContent: string,    // Updated content
 *   editedAt: string       // ISO timestamp of when it was edited
 * }
 */
export function editMessage(socket, chatId, messageId, newContent) {
    const payload = { 
        chatId, 
        messageId, 
        newContent };
    socket.emit('chat/message/edit', payload);
}

/**
 * Deletes a message from a chat group.
 * 
 * Server response (on `messageDeleted`):
 * {
 *   chatId: string,        // Identifier of the chat group
 *   messageId: string      // Identifier of the deleted message
 * }
 */
export function deleteMessage(socket, chatId, messageId) {
    const payload = { 
        chatId, 
        messageId };
    socket.emit('chat/message/delete', payload);
}

/**
 * Requests paginated message history for a chat group.
 * 
 * Server response (on `receiveMessage`):
 * {
 *   chatId: string,         // Identifier of the chat group
 *   page: number,           // Page number
 *   limit: number,          // Messages per page
 *   total: number,          // Total messages available
 *   messages: [             // Array of message objects as above
 *     { messageId, senderId, content, sentAt }, …
 *   ]
 * }
 */
export function fetchMessageHistory(socket, chatId, page = 1, limit = 20) {
    const payload = { 
        chatId, 
        page, 
        limit };
    socket.emit('chat/message/history', payload);
}
