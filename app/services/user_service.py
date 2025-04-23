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
        services_logger.info(f"Fetching affiliated chat list for user: {user_id}, page: {page}, limit: {limit}")

        try:
            if page < 1 or limit < 1:
                raise ValueError("Page and limit must be greater than zero")

            validate_id(user_id)

            all_group_ids = self.chat_groups_dal.get_all_chat_group_ids()
            services_logger.debug(f"Retrieved {len(all_group_ids)} total chat group IDs")

            affiliated_groups = []
            for group_id in all_group_ids:
                affiliation = ChatGroupsXMPP.get_user_affiliation_in_room(group_id, user_id)
                if affiliation and affiliation is not None:
                    affiliated_groups.append(group_id)

            total = len(affiliated_groups)
            services_logger.debug(f"User {user_id} is affiliated with {total} chat groups")

            start = (page - 1) * limit
            end = start + limit
            paginated_ids = affiliated_groups[start:end]

            chat_groups = []
            for group_id in paginated_ids:
                chat_group = self.chat_groups_dal.get_chat_group(group_id)
                if chat_group:
                    chat_groups.append({
                        "chatId": str(chat_group["_id"]),
                        "groupName": chat_group["groupName"],
                    })
                    services_logger.debug(f"Included group {group_id}")
                else:
                    chat_groups.append({"chatId": group_id, "groupName": None})
                    services_logger.warning(f"Metadata not found for group {group_id}")

            result = {
                "userId": user_id,
                "page": page,
                "limit": limit,
                "total": total,
                "chats": chat_groups
            }

            services_logger.info(f"✅ Successfully fetched chat list for user {user_id}")
            return result

        except Exception as e:
            services_logger.error(f"❌ Error in get_chat_list for user {user_id}: {e}")
            raise