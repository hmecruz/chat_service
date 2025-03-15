from utils.constants import *

def validate_group_name(group_name: str) -> str:
    """Validate group name with rules."""
    if not group_name:
        raise ValueError("Missing groupName field")
    if not isinstance(group_name, str):
        raise ValueError(f"Invalid groupName type {type(group_name)}. Expected string")
    if len(group_name) > MAX_GROUP_NAME_LENGTH:
        raise ValueError(f"groupName exceeds {MAX_GROUP_NAME_LENGTH} characters")
    return group_name

def validate_users(users: list) -> list:
    """Validate users list with rules."""
    if not users:
        raise ValueError("Missing users field")
    if not isinstance(users, list):
        raise ValueError("Invalid users type")
    if len(users) < MIN_USERS_REQUIRED:
        raise ValueError(f"At least {MIN_USERS_REQUIRED} users required")
    if len(users) > MAX_USERS_ALLOWED:
        raise ValueError(f"Maximum {MAX_USERS_ALLOWED} users allowed")
    
    for user in users:
        if not isinstance(user, str):
            raise ValueError(f"Invalid user type {type(user)}. Expected string")
        if len(user) > MAX_USER_ID_LENGTH:
            raise ValueError(f"User ID exceeds {MAX_USER_ID_LENGTH} characters")
    
    return users