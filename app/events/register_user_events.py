from flask import current_app
from flask_socketio import SocketIO
from ..events.user_events import UserEvents

def register_user_events(socketio: SocketIO):
    """
    Registers all user-related event handlers to the SocketIO instance."""

    user_events = UserEvents()

    socketio.on_event('user/chats', user_events.handle_get_chat_list)