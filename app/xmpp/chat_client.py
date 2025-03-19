import slixmpp
import logging
from slixmpp.exceptions import XMPPError
from flask_socketio import emit

class XMPPClient(slixmpp.ClientXMPP):
    def __init__(self, jid, password, websocket_url):
        super().__init__(jid, password)
        self.websocket_url = websocket_url
        self.connected = False

        # Register event handlers
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.handle_message)
        self.add_event_handler("presence", self.handle_presence)
        self.add_event_handler("disconnected", self.handle_disconnection)

        # Enable WebSocket connection
        self.add_event_handler("socketio_event", self.handle_socketio_event)

    async def start(self):
        """Start the XMPP session and establish connections."""
        self.connected = True
        logging.info("XMPP connection established.")
        
        # You can add initial tasks here (e.g., fetching presence, joining rooms, etc.)
        await self.get_roster()

    def handle_message(self, msg):
        """Handles incoming messages."""
        try:
            # Logic for processing incoming messages
            logging.info(f"Received message from {msg['from']}: {msg['body']}")
            
            # Prepare message data to emit to Flask-SocketIO clients
            message_data = {
                "from": msg['from'],
                "body": msg['body'],
                "sentAt": msg['timestamp']
            }

            # Emit event for new message to clients connected to WebSocket
            emit('receiveMessage', message_data, broadcast=True)
        except Exception as e:
            logging.error(f"Error handling message: {e}")

    def handle_presence(self, presence):
        """Handles presence updates (e.g., when a user joins or leaves)."""
        try:
            # Process user presence updates here
            logging.info(f"Received presence update: {presence['from']} is {presence['type']}")
            
            # Emit presence update event to WebSocket
            presence_data = {
                "from": presence['from'],
                "type": presence['type']
            }
            emit('presenceUpdate', presence_data, broadcast=True)
        except Exception as e:
            logging.error(f"Error handling presence: {e}")

    def handle_disconnection(self, *args):
        """Handles disconnection events."""
        self.connected = False
        logging.warning("Disconnected from XMPP server.")
        # You could trigger a reconnection mechanism here

    def handle_socketio_event(self, event_data):
        """Handles events from Flask-SocketIO."""
        try:
            # Process incoming events from WebSocket (SocketIO)
            logging.info(f"Received SocketIO event: {event_data}")
            
            # Handle the event (e.g., create chat room, send message, etc.)
            if event_data['event_type'] == 'create_chat':
                self.create_chat_group(event_data['chat_name'])
            elif event_data['event_type'] == 'send_message':
                self.send_message(event_data['chat_id'], event_data['message'])
        except Exception as e:
            logging.error(f"Error handling SocketIO event: {e}")

    def create_chat_group(self, chat_name):
        """Creates a new chat group (XMPP MUC room)."""
        try:
            logging.info(f"Creating chat group: {chat_name}")
            # XMPP MUC room creation logic here
            # Example: self.plugin['xep_0045'].joinMUC(room_jid, nick)
        except Exception as e:
            logging.error(f"Error creating chat group: {e}")

    def send_message(self, chat_id, message):
        """Sends a message to the XMPP server."""
        try:
            logging.info(f"Sending message to {chat_id}: {message}")
            # XMPP message sending logic
            self.send_message(mto=chat_id, mbody=message, mtype='chat')
        except Exception as e:
            logging.error(f"Error sending message: {e}")

    def connect_to_server(self):
        """Connect to the XMPP server."""
        try:
            # Connect to the server using WebSocket transport
            self.connect(self.websocket_url)
            self.process(forever=True)  # Run the event loop
        except XMPPError as e:
            logging.error(f"Error while connecting: {e}")
            raise

    def disconnect_from_server(self):
        """Disconnect the XMPP client."""
        if self.connected:
            self.disconnect()
            logging.info("Disconnected from XMPP server.")
