from flask import Flask
from flask_socketio import SocketIO
from app.events.chat_groups_events import *
from app.xmpp.manager import XMPPManager

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')

# Initialize XMPP manager
xmpp_manager = XMPPManager(jid='user@localhost', password='password', db_instance=some_db_instance, websocket_url='ws://localhost:5280/xmpp-websocket')

# Start the XMPP session when the app starts
@app.before_first_request
def start_xmpp():
    xmpp_manager.start_xmpp_session()

if __name__ == '__main__':
    socketio.run(app, debug=True)
