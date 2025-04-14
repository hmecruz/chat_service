import ssl
import logging

import slixmpp
from slixmpp.exceptions import XMPPError


class XMPPClient(slixmpp.ClientXMPP):
    def __init__(self, jid, password: str, use_certificate : bool = True):
        """Initialize the XMPP client"""
        super().__init__(jid, password)

        if not use_certificate:
            self.ssl_context = ssl.create_default_context() # TODO Check if correct
            self.ssl_context.check_hostname=False
            self.ssl_context.verify_mode=ssl.CERT_NONE

        # Plugins
        self.register_plugin('xep_0030')  # Service Discovery
        self.register_plugin('xep_0045')  # Multi-User Chat
        self.register_plugin('xep_0199')  # XMPP Ping

        # Register event handlers
        self.add_event_handler("session_start", self.session_start)   
        

    async def session_start(self):
        """Start the XMPP session and establish connections."""
        self.send_presence()
        await self.get_roster()


    def client_presence(self):  
        """Check if the client is connected"""
        return self.is_connected()

    
    def connect_to_server(self, host: str, port: int, use_ssl: bool, force_starttls: bool):
        """Connect to the XMPP server with given parameters."""
        try:
            return self.connect(address=(host, port), use_ssl=use_ssl, force_starttls=force_starttls)
        except XMPPError as e:
            logging.error(f"❌ Connection failed: {e}")


    def disconnect_from_server(self):
        """Disconnect the XMPP client."""
        self.disconnect()
