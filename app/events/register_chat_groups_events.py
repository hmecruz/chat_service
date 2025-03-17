from flask import current_app
from flask_socketio import SocketIO
from app.events.chat_groups_events import ChatGroupsEvents

def register_chat_group_events(socketio: SocketIO):
    """
    Registers all chat group-related event handlers to the SocketIO instance.
    """

    xmpp_client = current_app.config['xmpp_client']

    chat_groups_events = ChatGroupsEvents(xmpp_client)

    socketio.on_event('chat/create', chat_groups_events.handle_create_chat)
    socketio.on_event('chat/name/update', chat_groups_events.handle_update_chat_name)
    socketio.on_event('chat/delete', chat_groups_events.handle_delete_chat)
    socketio.on_event('chat/users/add', chat_groups_events.handle_add_users)
    socketio.on_event('chat/users/remove', chat_groups_events.handle_remove_users)