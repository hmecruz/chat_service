import logging
from slixmpp.exceptions import IqError, IqTimeout

class ChatGroupsXMPP:
    """Class for handling chat groups in XMPP."""
    def __init__(self, xmpp_client):
        self.xmpp_client = xmpp_client

    async def create_chat_group(self, room_jid: str, nickname: str):
        """
        Creates a chat group (MUC) by joining (or creating) a room on the XMPP server.
        
        Args:
            room_jid (str): The JID for the chat room (e.g., "team_chat@conference.example.com").
            nickname (str): The nickname to use in the room.
        
        Returns:
            room_jid if successful; raises an exception otherwise.
        """
        try:
            muc_plugin = self.xmpp_client.plugin['xep_0045']
            await muc_plugin.join_muc(room_jid, nickname)
            logging.info("Joined (or created) XMPP group: %s", room_jid)
            return room_jid
        except IqError as e:
            error_text = e.iq['error']['text'] if e.iq['error']['text'] else "Unknown error"
            logging.error("Failed to create XMPP group: %s", error_text)
            raise Exception(f"XMPP group creation error: {error_text}")
        except IqTimeout:
            logging.error("Timeout while creating XMPP group: %s", room_jid)
            raise Exception("XMPP group creation timeout")
        

    async def add_users_to_group(self, chat_id, user_ids):
        """Add users to an existing chat group."""
        result = self.chat_groups_service.add_users_to_chat(chat_id, user_ids)
        logging.info("Added users %s to chat group %s", user_ids, chat_id)
        return result

    async def remove_users_from_group(self, chat_id, user_ids):
        """Remove users from an existing chat group."""
        result = self.chat_groups_service.remove_users_from_chat(chat_id, user_ids)
        logging.info("Removed users %s from chat group %s", user_ids, chat_id)
        return result

    async def delete_chat_group(self, chat_id):
        """Delete a chat group."""
        result = self.chat_groups_service.delete_chat_group(chat_id)
        logging.info("Deleted chat group %s: %s", chat_id, result)
        return result