import logging

import requests
from requests.auth import HTTPBasicAuth

from slixmpp.exceptions import XMPPError
from config.xmpp_config import XMPPConfig

class ChatGroupsXMPP:
    def __init__(self):
        pass

    def handle_socketio_event(self, event_data):
        """Handles events from Flask-SocketIO related to chat groups."""
        pass

    def create_chat_group(self, chat_id: str):
        """Create a new XMPP chat group (MUC room)."""
        endpoint = f"{XMPPConfig.EJABBERD_API_URL}/create_room"
        payload = {
            "room": chat_id,
            "service": XMPPConfig.MUC_SERVICE,
            "host": XMPPConfig.VHOST
        }
        try:
            response = requests.post(
                endpoint,
                json=payload,
                auth=HTTPBasicAuth(XMPPConfig.ADMIN_USER, XMPPConfig.ADMIN_PASSWORD),
                verify=False
            )
            response.raise_for_status()
            logging.info(f"✅ Room {chat_id}@{XMPPConfig.MUC_SERVICE} created successfully.")
            
            return True
        
        except requests.RequestException as e:
            logging.error(f"❌ Failed to create room {chat_id}@{XMPPConfig.MUC_SERVICE}: {e}")
            return False
    
    def delete_chat_group(self, chat_id: str):
        """Delete an XMPP chat group (MUC room)."""
        endpoint = f"{XMPPConfig.EJABBERD_API_URL}/destroy_room"
        payload = {
            "room": chat_id,
            "service": XMPPConfig.MUC_SERVICE
        }
        try:
            response = requests.post(
                endpoint,
                json=payload,
                auth=HTTPBasicAuth(XMPPConfig.ADMIN_USER, XMPPConfig.ADMIN_PASSWORD),
                verify=False
            )
            response.raise_for_status()
            logging.info(f"🗑️ Room {chat_id}@{XMPPConfig.MUC_SERVICE} destroyed successfully.")
            return True
        except requests.RequestException as e:
            logging.error(f"❌ Failed to destroy room {chat_id}@{XMPPConfig.MUC_SERVICE}: {e}")
            return False
        
        
    def configure_room(self, xmpp_client, room_jid: str):
        """Optionally configure a room's settings using XMPP."""
        try:
            form = xmpp_client.plugin['xep_0045'].get_room_config(room_jid)
            form.set_values({
                'muc#roomconfig_persistentroom': True,
                'muc#roomconfig_publicroom': False,
                'muc#roomconfig_membersonly': True,
                'muc#roomconfig_allowinvites': True,
            })
            self.xmpp_client.plugin['xep_0045'].configure_room(room_jid, form)
            logging.info(f"⚙️ Room {room_jid} configured successfully.")
        except XMPPError as e:
            logging.error(f"❌ Failed to configure room {room_jid}: {e}")
