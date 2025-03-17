from flask import current_app
from flask_socketio import SocketIO
from app.events.chat_messages_events import ChatMessagesEvents

def register_chat_message_events(socketio: SocketIO):
    """
    Registers all chat message-related event handlers to the SocketIO instance.
    """

    xmpp_client = current_app.config['xmpp_client']

    chat_messages_events = ChatMessagesEvents(xmpp_client)

    socketio.on_event('chat/message', chat_messages_events.handle_send_message)
    socketio.on_event('chat/message/edit', chat_messages_events.handle_edit_message)
    socketio.on_event('chat/message/delete', chat_messages_events.handle_delete_message)
    socketio.on_event('chat/message/history', chat_messages_events.handle_message_history)