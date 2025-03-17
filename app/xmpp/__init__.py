import logging
from flask import current_app 
from threading import Thread
from .chat_client import ChatClient
from .chat_groups_xmpp import ChatGroupsXMPP
from .chat_messages_xmpp import ChatMessagesXMPP

def initialize_xmpp_client(jid, password, websocket_url):
    xmpp_client = ChatClient(jid, password, websocket_url)
    current_app.config['xmpp_client'] = xmpp_client
    current_app.config['chat_groups_xmpp'] = ChatGroupsXMPP(xmpp_client)
    current_app.config['chat_messages_xmpp'] = ChatMessagesXMPP(xmpp_client)

    def start_client():
        try:
            xmpp_client.connect()
            xmpp_client.process(forever=True)
        except Exception as e:
            logging.error("Failed to start XMPP client: %s", e)

    xmpp_thread = Thread(target=start_client)
    xmpp_thread.daemon = True
    xmpp_thread.start()

    return xmpp_client