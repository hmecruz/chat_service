/**
 * Requests the list of chats for a user (paginated).
 * 
 * Server response (on `getUserChats`):
 * {
 *   userId: string,        // Identifier of the user
 *   page: number,          // Page number
 *   limit: number,         // Chats per page
 *   total: number,         // Total chats available
 *   chats: [               // Array of chat group summaries
 *     { chatId: string, groupName: string }, …
 *   ]
 * }
 */
export function fetchUserChats(socket, userId, page = 1, limit = 20) {
    const payload = { userId, page, limit };
    socket.emit('user/chats', payload);
}