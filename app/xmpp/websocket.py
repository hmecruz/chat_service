import json
from flask_socketio import SocketIO, emit
from app.xmpp.manager import XMPPManager
from bson.objectid import ObjectId

# Example WebSocket handler
@socketio.on('chat/{chatId}/message')
def handle_chat_message(data):
    xmpp_manager = XMPPManager(jid='user@localhost', password='password', db_instance=some_db_instance, websocket_url='ws://localhost:5280/xmpp-websocket')
    
    # Store message in database (use your database handling code here)
    result = xmpp_manager.store_message(ObjectId(data['payload']['chatId']), data['payload']['senderId'], data['payload']['content'])
    
    # Send message to XMPP MUC
    xmpp_manager.send_message('testroom@conference.localhost', data['payload']['content'])
    
    emit('chat/{chatId}/message/event', {"payload": result})
