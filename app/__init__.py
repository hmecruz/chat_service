from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_socketio import SocketIO

from .database.database_init import ChatServiceDatabase
from .database.chat_groups import ChatGroups
from .database.chat_messages import ChatMessages

from .services.chat_groups_services import ChatGroupsService
from .services.chat_messages_services import ChatMessagesService

from .events.register_chat_groups_events import register_chat_group_events
from .events.register_chat_messages_events import register_chat_message_events

from .xmpp.client_registry import XMPPClientRegistry

# Create a global SocketIO instance
socketio = SocketIO(cors_allowed_origins="*")

def create_app():

    app = Flask(__name__)
    # Load configuration from a config file or object
    app.config.from_object('config.service_config')  # Adjust as required

    # Initialize SocketIO with the app instance
    socketio.init_app(app)

    # Initialize database connection
    db = ChatServiceDatabase()
    app.config['db'] = db

    # Instantiate ChatGroupsService
    chat_groups_dal = ChatGroups(db)
    chat_groups_service = ChatGroupsService(chat_groups_dal)

    chat_messages_dal = ChatMessages(db)
    chat_messages_service = ChatMessagesService(chat_messages_dal)

    app.config['chat_groups_service'] = chat_groups_service
    app.config['chat_messages_service'] = chat_messages_service 

    
    # Instantiate the XMPPClients registry
    xmpp_clients = XMPPClientRegistry()
    app.config['xmpp_clients'] = xmpp_clients

    with app.app_context():
        #initialize_xmpp_client(XmppConfig.JID, XmppConfig.PASSWORD, XmppConfig.WEBSOCKET_URL)
        register_chat_group_events(socketio)
        register_chat_message_events(socketio)

    # Ensure DB connection is closed on shutdown
    @app.teardown_appcontext
    def close_db_connection(exception=None):
        db.close_connection()

    return app
