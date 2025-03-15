import asyncio
import logging
import json
import slixmpp
from slixmpp.exceptions import IqError, IqTimeout
from slixmpp.xmlstream.stanzas import Message, Iq
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from bson.objectid import ObjectId
from datetime import datetime, UTC

from database.database_init import ChatServiceDatabase
from database.chat_groups import ChatGroups
from database.chat_messages import ChatMessages

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)-8s %(message)s')

# Initialize Flask app and SocketIO
app = Flask(__name__)
socketio = SocketIO(app)

class ChatClient(slixmpp.ClientXMPP):
    def __init__(self, jid, password, websocket_url, db_instance):
        super().__init__(jid, password)
        self.websocket_url = websocket_url
        self.db_instance = db_instance
        self.chat_groups_dal = ChatGroups(db_instance)
        self.chat_messages_dal = ChatMessages(db_instance)
        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message)
        self.add_event_handler("disconnected", self.disconnected)
        self.register_plugin('xep_0030')  # Service Discovery
        self.register_plugin('xep_0199')  # XMPP Ping
        self.register_plugin('xep_0045')  # Multi-User Chat (MUC)
        self.add_event_handler("muc::%s::got_presence" % 'testroom@conference.localhost', self.muc_presence)
        self.add_event_handler("muc::%s::message" % 'testroom@conference.localhost', self.muc_message)

    async def session_start(self, event):
        self.send_presence()
        await self.get_roster()
        logging.info("Session started")
        try:
            await self.plugin['xep_0045'].join_muc('testroom@conference.localhost', 'MyNick')
            logging.info("Joined MUC testroom@conference.localhost")
        except IqError as err:
            logging.error("Could not join MUC: %s" % err.iq['error']['text'])
        except IqTimeout:
            logging.error("No response from MUC server.")

    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            logging.info(f"Received message: {msg['body']} from {msg['from']}")

    def muc_presence(self, presence):
        logging.info(f"MUC presence: {presence['from']} - {presence['type']}")

    def muc_message(self, msg):
        if msg['type'] in ('groupchat'):
            logging.info(f"MUC message: {msg['body']} from {msg['from']}")

    def disconnected(self, event):
        logging.info("Disconnected from server.")

    async def send_muc_message(self, room_jid, message):
        msg = self.Message()
        msg['to'] = room_jid
        msg['type'] = 'groupchat'
        msg['body'] = message
        msg.send()

# Flask-SocketIO event handler
@socketio.on('chat/create')
def handle_chat_create(data):
    chat_groups_dal = ChatGroups(ChatServiceDatabase())
    result = chat_groups_dal.create_chat_group(data['payload']['groupName'], data['payload']['users'])
    emit('chat/create/event', {"payload": result})

@socketio.on('chat/{chatId}/users/add')
def handle_add_users(data):
    chat_groups_dal = ChatGroups(ChatServiceDatabase())
    result = chat_groups_dal.add_users_to_chat(ObjectId(data['payload']['chatId']), data['payload']['userIds'])
    emit('chat/{chatId}/users/add/event', {"payload": result})

@socketio.on('chat/{chatId}/message')
def handle_chat_message(data):
    chat_messages_dal = ChatMessages(ChatServiceDatabase())
    result = chat_messages_dal.store_message(
        ObjectId(data['payload']['chatId']),
        data['payload']['senderId'],
        data['payload']['content']
    )
    emit('chat/{chatId}/message/event', {"payload": result})

    # Send the message to the XMPP MUC room
    xmpp_client.send_muc_message('testroom@conference.localhost', data['payload']['content'])

@socketio.on('chat/{chatId}/message/edit')
def handle_edit_message(data):
    chat_messages_dal = ChatMessages(ChatServiceDatabase())
    result = chat_messages_dal.edit_message(ObjectId(data['payload']['messageId']), data['payload']['newContent'])
    emit('chat/{chatId}/message/edit/event', {"payload": result})

@socketio.on('chat/{chatId}/message/delete')
def handle_delete_message(data):
    chat_messages_dal = ChatMessages(ChatServiceDatabase())
    result = chat_messages_dal.delete_message(ObjectId(data['payload']['messageId']))
    emit('chat/{chatId}/message/delete/event', {"payload": {"messageId": data['payload']['messageId'], "deletedCount": result}})

@socketio.on('chat/{chatId}/message/history')
def handle_message_history(data):
    chat_messages_dal = ChatMessages(ChatServiceDatabase())
    result = chat_messages_dal.get_messages(ObjectId(data['payload']['chatId']), data['payload']['page'], data['payload']['limit'])
    emit('chat/{chatId}/message/history/event', {"payload": result})

@socketio.on('user/{userId}/chats')
def handle_user_chats(data):
    chat_groups_dal = ChatGroups(ChatServiceDatabase())
    result = chat_groups_dal.get_chat_groups_for_user(data['payload']['userId'], data['payload']['page'], data['payload']['limit'])
    emit('user/{userId}/chats/event', {"payload": result})

# Initialize and run the Flask-SocketIO server
def run_flask_app():
    # XMPP Client Setup
    jid = 'user@localhost'
    password = 'password'
    websocket_url = 'ws://localhost:5280/xmpp-websocket'
    db_instance = ChatServiceDatabase()
    xmpp = ChatClient(jid, password, websocket_url, db_instance)
    xmpp.use_websockets(websocket_url)
    asyncio.create_task(xmpp.connect(use_tls=False))
    socketio.run(app, host="localhost", port=5000)

if __name__ == '__main__':
    run_flask_app()
