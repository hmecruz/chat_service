import logging
from flask import current_app 
from threading import Thread
from app.xmpp.chat_client import ChatClient
from config.xmpp_config import XmppConfig
from xmpp.chat_groups_xmpp import ChatGroupsXMPP
from xmpp.chat_messages_xmpp import ChatMessagesXMPP

def initialize_xmpp_client():
    xmpp_client = ChatClient(XmppConfig.JID, XmppConfig.PASSWORD, XmppConfig.WEBSOCKET_URL)
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