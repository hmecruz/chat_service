import logging
import slixmpp
from slixmpp.exceptions import IqError, IqTimeout

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)-8s %(message)s')

class ChatClient(slixmpp.ClientXMPP):
    def __init__(self, jid, password, websocket_url):
        super().__init__(jid, password)
        self.websocket_url = websocket_url

        # Register XMPP event handlers
        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message)
        self.add_event_handler("disconnected", self.disconnected)

        # Register plugins for XMPP functionalities
        self.register_plugin('xep_0030')  # Service Discovery
        self.register_plugin('xep_0199')  # XMPP Ping
        self.register_plugin('xep_0045')  # Multi-User Chat (MUC)

        # Example: register MUC event handlers for a test room.
        self.add_event_handler("muc::testroom@conference.localhost::got_presence", self.muc_presence)
        self.add_event_handler("muc::testroom@conference.localhost::message", self.muc_message)

    async def session_start(self, event):
        """Called when the XMPP session is started."""
        self.send_presence()
        await self.get_roster()
        logging.info("XMPP session started")
        # Optionally join a default MUC room (adjust as needed)
        try:
            await self.plugin['xep_0045'].join_muc('testroom@conference.localhost', 'MyNick')
            logging.info("Joined MUC testroom@conference.localhost")
        except IqError as err:
            logging.error("Could not join MUC: %s", err.iq['error']['text'])
        except IqTimeout:
            logging.error("No response from MUC server.")

    def message(self, msg):
        """Handles incoming messages."""
        if msg['type'] in ('chat', 'normal'):
            logging.info(f"Message from {msg['from']}: {msg['body']}")

    def muc_presence(self, presence):
        logging.info("MUC presence: %s - %s", presence['from'], presence.get('type', 'available'))

    def muc_message(self, msg):
        if msg['type'] == 'groupchat':
            logging.info("MUC message: %s from %s", msg['body'], msg['from'])

    def disconnected(self, event):
        logging.info("Disconnected from XMPP server.")


    # -------------------------------
    # XMPP-Specific Methods
    # -------------------------------

    async def send_muc_message(self, room_jid, message):
        """
        Send a groupchat message to a specified room.
        """
        msg = self.Message()
        msg['to'] = room_jid
        msg['type'] = 'groupchat'
        msg['body'] = message
        msg.send()
        logging.info("Sent MUC message to %s: %s", room_jid, message)
