import logging
from slixmpp.exceptions import IqError, IqTimeout

class ChatGroupsXMPP:
    """Class for handling XMPP chat groups."""
    
    def __init__(self, xmpp_client):
        self.xmpp_client = xmpp_client

    async def create_chat_group(self, room_jid: str, nickname: str):
        """
        Creates a chat group (MUC) by joining a room on the XMPP server.
        
        Args:
            room_jid (str): The JID for the chat room (e.g., "group_chat@conference.example.com").
            nickname (str): The nickname to use in the room.
        
        Returns:
            str: The room JID if successful.
        """
        try:
            muc_plugin = self.xmpp_client.plugin['xep_0045']
            await muc_plugin.join_muc(room_jid, nickname)
            logging.info(f"Created or joined XMPP group: {room_jid}")
            return room_jid
        except IqError as e:
            error_text = e.iq['error']['text'] if e.iq['error']['text'] else "Unknown error"
            logging.error(f"Failed to create XMPP group: {error_text}")
            raise Exception(f"XMPP group creation error: {error_text}")
        except IqTimeout:
            logging.error(f"Timeout while creating XMPP group: {room_jid}")
            raise Exception("XMPP group creation timeout")

    async def add_user_to_group(self, room_jid: str, user_jid: str):
        """Adds a user to the chat group."""
        try:
            muc_plugin = self.xmpp_client.plugin['xep_0045']
            await muc_plugin.invite(room_jid, user_jid)
            logging.info(f"Invited {user_jid} to {room_jid}")
        except Exception as e:
            logging.error(f"Error inviting user to XMPP group: {e}")
            raise Exception("Failed to add user to group")