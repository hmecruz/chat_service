import logging
from flask import current_app 
from threading import Thread
from app.xmpp.client import ChatClient
from config.xmpp_config import XmppConfig

def initialize_xmpp_client():
    db = current_app.config['db']
    xmpp_client = ChatClient(XmppConfig.JID, XmppConfig.PASSWORD, XmppConfig.WEBSOCKET_URL, db)
    current_app.config['xmpp_client'] = xmpp_client

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