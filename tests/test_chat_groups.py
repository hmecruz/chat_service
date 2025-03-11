from datetime import datetime
from bson.objectid import ObjectId

def test_create_chat_group(chat_groups):
    """Test creating a chat group."""
    group_name = "Test Group"
    users = ["user1", "user2"]
    
    chat_group = chat_groups.create_chat_group(group_name, users)
    
    assert chat_group is not None
    print(chat_group)
    assert isinstance(chat_group["_id"], ObjectId)
    assert chat_group["groupName"] == group_name
    assert set(chat_group["users"]) == set(users)
    assert isinstance(chat_group["createdAt"], datetime)

def test_get_chat_group(chat_groups):
    """Test retrieving a chat group."""
    group_name = "Test Group"
    users = ["user1", "user2"]
    
    create_chat_group = chat_groups.create_chat_group(group_name, users)
    print(create_chat_group)
    assert create_chat_group is not None
    assert isinstance(create_chat_group["_id"], ObjectId)
    assert create_chat_group["groupName"] == group_name
    assert set(create_chat_group["users"]) == set(users)
    assert isinstance(create_chat_group["createdAt"], datetime)

    get_chat_group = chat_groups.get_chat_group(create_chat_group["_id"])
    print(get_chat_group)
    assert get_chat_group is not None
    assert isinstance(create_chat_group["_id"], ObjectId)
    assert create_chat_group["_id"] == get_chat_group["_id"]
    assert create_chat_group["groupName"] == get_chat_group["groupName"]
    assert set(create_chat_group["users"]) == set(get_chat_group["users"])
    assert create_chat_group["createdAt"] == get_chat_group["createdAt"]


def test_update_chat_group(chat_groups):
    """Test updating a chat group."""
    chat_id = chat_groups.create_chat_group("Old Name", ["user1"])
    chat_groups.update_chat_group(chat_id, group_name="New Name", users=["user1", "user2"])
    
    updated_group = chat_groups.get_chat_group(chat_id)
    assert updated_group["groupName"] == "New Name"
    assert set(updated_group["users"]) == {"user1", "user2"}


def test_delete_chat_group(chat_groups):
    """Test deleting a chat group."""
    chat_id = chat_groups.create_chat_group("ToDelete", ["user1"])
    chat_groups.delete_chat_group(chat_id)

    assert chat_groups.get_chat_group(chat_id) is None


def test_add_remove_user(chat_groups):
    """Test adding and removing a user from a chat group."""
    chat_id = chat_groups.create_chat_group("Test Group", ["user1"])
    
    chat_groups.add_user_to_chat(chat_id, "user2")
    assert "user2" in chat_groups.get_chat_group(chat_id)["users"]

    chat_groups.remove_user_from_chat(chat_id, "user2")
    assert "user2" not in chat_groups.get_chat_group(chat_id)["users"]


def test_get_chat_groups_for_user(chat_groups):
    """Test retrieving chat groups for a user."""
    chat_groups.create_chat_group("Group1", ["user1"])
    chat_groups.create_chat_group("Group2", ["user1", "user2"])
    
    groups = chat_groups.get_chat_groups_for_user("user1")
    assert len(groups) == 2
