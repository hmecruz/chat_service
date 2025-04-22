from ..xmpp.chat_groups_xmpp import ChatGroupsXMPP
from ..utils.validators import validate_id
from .logger import services_logger

class UserService:
    def __init__(self, chat_groups_dal):
        self.chat_groups_dal = chat_groups_dal
        self.chat_groups_xmpp = ChatGroupsXMPP()

    def get_chat_list(self, user_id: str, page: int = 1, limit: int = 20) -> dict:
        """
        Retrieves a paginated list of chat groups (MUC rooms) for a given user via XMPP.

        Args:
            user_id (str): The ID of the user.
            page (int): Page number for pagination.
            limit (int): Number of items per page.

        Returns:
            dict: Contains total number of rooms and list of chat group metadata.
        """
        services_logger.info(f"Fetching chat list for user: {user_id}, page: {page}, limit: {limit}")

        try:
            if page < 1 or limit < 1:
                raise ValueError("Page and limit must be greater than zero")
            services_logger.debug(f"Validated pagination parameters: page={page}, limit={limit}")
            
            validate_id(user_id)
            services_logger.debug(f"Validated user_id: {user_id}")

            # Fetch all XMPP rooms this user is in
            all_rooms_full_jid = self.chat_groups_xmpp.get_user_rooms(user_id)
            services_logger.debug(f"Fetched all rooms for user {user_id}: {all_rooms_full_jid}")

            all_room_ids = [room.split("@")[0] for room in all_rooms_full_jid if "@" in room]
            total = len(all_room_ids)
            services_logger.debug(f"Total rooms for user {user_id}: {total}")

            # Paginate
            start = (page - 1) * limit
            end = start + limit
            paginated_room_ids = all_room_ids[start:end]
            services_logger.debug(f"Paginated room IDs: {paginated_room_ids}")

            # Fetch metadata from DB for each room
            chat_groups = []
            for room_id in paginated_room_ids:
                chat_group = self.chat_groups_dal.get_chat_group(room_id)
                if chat_group:
                    chat_groups.append({
                        "chatId": str(chat_group["_id"]),
                        "groupName": chat_group["groupName"],
                    })
                    services_logger.debug(f"Fetched metadata for room {room_id}")
                else:
                    # Fallback if room metadata isn't found
                    chat_groups.append({"chatId": room_id, "groupName": None})
                    services_logger.warning(f"Metadata not found for room {room_id}")

            result = {
                "userId": user_id,
                "page": page,
                "limit": limit,
                "total": total,
                "chats": chat_groups
            }

            services_logger.info(f"Successfully fetched chat list for user {user_id}")
            return result
        except Exception as e:
            services_logger.error(f"Error fetching chat list for user {user_id}: {e}")
            raise
