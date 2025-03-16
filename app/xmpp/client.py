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
