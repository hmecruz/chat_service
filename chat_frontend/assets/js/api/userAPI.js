export function fetchUserChats(socket, userId, page = 1, limit = 20) {
    const payload = {
        userId, // The user requesting the chat list
        page,   // Pagination: page number
        limit   // Pagination: number of chats per page
    };

    // Emit the event to fetch the chat list
    socket.emit('user/chats', payload);
}