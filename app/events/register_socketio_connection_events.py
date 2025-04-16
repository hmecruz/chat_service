from flask_socketio import SocketIO
from ..events.socketio_connection_events import SocketIOConnectionEvents

def register_socketio_connection_events(socketio: SocketIO):
    """
    Registers all SocketIO connection-related event handlers to the SocketIO instance.
    """

    socketio_connection_events = SocketIOConnectionEvents()

    socketio.on_event('connect', socketio_connection_events.handle_connect)
    