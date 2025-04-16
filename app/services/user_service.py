from ..xmpp.chat_groups_xmpp import ChatGroupsXMPP
from ..utils.validators import validate_id

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
        if page < 1 or limit < 1:
            raise ValueError("Page and limit must be greater than zero")
        validate_id(user_id)

        # Fetch all XMPP rooms this user is in
        all_rooms = self.chat_groups_xmpp.get_user_rooms(user_id)
        total = len(all_rooms)

        # Paginate
        start = (page - 1) * limit
        end = start + limit
        paginated_rooms = all_rooms[start:end]

        # Fetch metadata from DB for each room if available
        chat_groups = []
        for room_id in paginated_rooms:
            chat_group = self.chat_groups_dal.get_chat_group(room_id)
            if chat_group:
                chat_groups.append({
                    "chatId": str(chat_group["_id"]),
                    "groupName": chat_group["groupName"],
                })
            else:
                # Fallback to show room ID only if DB lookup fails
                chat_groups.append({"chatId": room_id, "groupName": None})

        return {
            "userId": user_id,
            "page": page,
            "limit": limit,
            "total": total,
            "chats": chat_groups
        }
