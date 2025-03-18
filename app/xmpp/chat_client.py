import asyncio
import logging
import slixmpp
from slixmpp.exceptions import IqError, IqTimeout

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)-8s %(message)s')

class ChatClient(slixmpp.ClientXMPP):
    def __init__(self, jid, password):
        super().__init__(jid, password)

        # Register event handlers
        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message_received)
        self.add_event_handler("disconnected", self.disconnected)

        # Register XMPP plugins
        self.register_plugin('xep_0030')  # Service Discovery
        self.register_plugin('xep_0199')  # XMPP Ping
        self.register_plugin('xep_0045')  # Multi-User Chat (MUC)

    
    async def start(self, event):
        """Handle session start event."""
        self.send_presence()
        await self.get_roster()

    async def connect(self):
        """Connect to the XMPP server."""
        await super().connect()  # Directly await it instead of passing to create_task


    async def wait_until_connected(self):
        """Waits until the client is fully connected."""
        while not self.is_connected():
            await asyncio.sleep(0.1)  # Small delay to prevent busy-waiting

    async def disconnect(self):
        """Asynchronous disconnect method."""
        self.disconnect()
    
    async def session_start(self, event):
        """Called when the XMPP session is started."""
        self.send_presence()
        await self.get_roster()
        logging.info(f"XMPP session started for {self.boundjid.bare}")

    def message_received(self, msg):
        """Handles incoming messages."""
        if msg['type'] in ('chat', 'normal', 'groupchat'):
            logging.info(f"Message from {msg['from']}: {msg['body']}")

    def disconnected(self, event):
        logging.info("Disconnected from XMPP server.")
