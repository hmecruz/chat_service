import pytest
from datetime import datetime, UTC
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

    created_chat_group = chat_groups.chat_groups.find_one({"_id": chat_group["_id"]})
    assert created_chat_group is not None
    assert created_chat_group["_id"] == chat_group["_id"]
    assert created_chat_group["groupName"] == chat_group["groupName"]
    assert set(created_chat_group["users"]) == set(chat_group["users"])
    assert created_chat_group["createdAt"] == chat_group["createdAt"]


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


def test_update_chat_group_name(chat_groups):
    """Test updating a chat group's name."""
    original_name = "Original Group Name"
    new_name = "Updated Group Name"
    users = ["user1", "user2"]

    # Create a chat group with the original name.
    chat_group = chat_groups.create_chat_group(original_name, users)
    chat_id = chat_group["_id"]

    # Update the chat group's name.
    update_result = chat_groups.update_chat_group_name(chat_id, new_name)

    # Verify the returned dictionary contains the expected values.
    assert isinstance(update_result, dict)
    assert update_result["_id"] == chat_id
    assert update_result["groupName"] == new_name

    # Retrieve the updated group from the database and verify the change.
    updated_group = chat_groups.get_chat_group(chat_id)
    assert updated_group is not None
    assert updated_group["groupName"] == new_name


def test_delete_chat_group(chat_groups):
    """Test deleting an existing chat group and attempting to delete a non-existent group."""
    # Delete an Existing Group 
    created_group = chat_groups.create_chat_group("ToDelete", ["user1"])
    chat_id = created_group["_id"]

    # Delete the group and verify one document was removed
    deleted_count = chat_groups.delete_chat_group(chat_id)
    assert deleted_count == 1, "Expected one document to be deleted."
    # Confirm that the group no longer exists in the database
    assert chat_groups.get_chat_group(chat_id) is None, "Group should be deleted."

    # Attempt to Delete a Non-existent Group 
    fake_chat_id = ObjectId()  # Generate a new ObjectId that does not exist
    deleted_count_non_existent = chat_groups.delete_chat_group(fake_chat_id)
    assert deleted_count_non_existent == 0, "Expected no document to be deleted for a non-existent group."


def test_add_users_to_chat(chat_groups):
    """Test adding multiple users to a chat group."""
    original_group = chat_groups.create_chat_group("Test Group", ["user1"])
    chat_id = original_group["_id"]

    updated_info = chat_groups.add_users_to_chat(chat_id, ["user2", "user3"])
    assert isinstance(updated_info, dict)
    assert updated_info["_id"] == chat_id
    assert set(updated_info["users"]) == {"user1", "user2", "user3"}

    # Test adding users that already exist (should not duplicate)
    updated_info = chat_groups.add_users_to_chat(chat_id, ["user2", "user4"])
    assert set(updated_info["users"]) == {"user1", "user2", "user3", "user4"}


def test_remove_users_from_chat(chat_groups):
    """Test removing multiple users from a chat group."""
    original_group = chat_groups.create_chat_group("Test Group", ["user1", "user2", "user3"])
    chat_id = original_group["_id"]

    updated_info = chat_groups.remove_users_from_chat(chat_id, ["user2", "user3"])
    assert isinstance(updated_info, dict)
    assert updated_info["_id"] == chat_id
    assert updated_info["users"] == ["user1"]

    # Test removing a user that is not in the group (should not affect data)
    updated_info = chat_groups.remove_users_from_chat(chat_id, ["user4"])
    assert updated_info["users"] == ["user1"]


def test_add_users_to_chat_empty_list(chat_groups):
    """Test adding an empty list of users does nothing."""
    original_group = chat_groups.create_chat_group("Test Group", ["user1"])
    chat_id = original_group["_id"]

    updated_info = chat_groups.add_users_to_chat(chat_id, [])
    assert isinstance(updated_info, dict)
    assert updated_info["_id"] == chat_id
    assert updated_info["users"] == ["user1"]  # No change


def test_remove_users_from_chat_empty_list(chat_groups):
    """Test removing an empty list of users does nothing."""
    original_group = chat_groups.create_chat_group("Test Group", ["user1", "user2"])
    chat_id = original_group["_id"]

    updated_info = chat_groups.remove_users_from_chat(chat_id, [])
    assert isinstance(updated_info, dict)
    assert updated_info["_id"] == chat_id
    assert set(updated_info["users"]) == {"user1", "user2"}  # No change


def test_get_chat_groups_for_user_no_groups(chat_groups):
    """Test that querying for a user with no groups returns an empty list."""
    # Query a user that does not exist in any group.
    result = chat_groups.get_chat_groups_for_user("nonexistent_user", page=1, limit=5)
    assert isinstance(result, list)
    assert len(result) == 0


def test_get_chat_groups_for_user_pagination(chat_groups):
    """
    Test retrieving a paginated list of chat groups for a given user.
    
    This test creates 10 chat groups with "user1" as a member.
    It then verifies:
      - Page 1 returns 5 groups.
      - Page 2 returns 5 groups.
      - Page 3 returns an empty list.
      - Each returned document contains "_id" as a ObjectId and "user1" in its "users" list.
    """
    # Create 10 chat groups where "user1" is always a member.
    total_groups = 10
    for i in range(total_groups):
        group_name = f"Group {i+1}"
        # Include "user1" plus another unique user for diversity.
        chat_groups.create_chat_group(group_name, ["user1", f"user{i+2}"])

    # Retrieve paginated results.
    page1 = chat_groups.get_chat_groups_for_user("user1", page=1, limit=5)
    page2 = chat_groups.get_chat_groups_for_user("user1", page=2, limit=5)
    page3 = chat_groups.get_chat_groups_for_user("user1", page=3, limit=5)

    # Check that page1 and page2 return 5 groups each, and page3 returns none.
    assert len(page1) == 5, "Page 1 should return 5 groups"
    assert len(page2) == 5, "Page 2 should return 5 groups"
    assert len(page3) == 0, "Page 3 should return 0 groups"

    # Verify that each returned group contains "user1" and has a proper chat_id.
    for group in page1 + page2:
        assert "user1" in group.get("users", []), "The group must include 'user1'"
        assert "_id" in group, "The group should have a '_id' field"
        # Ensure that _id is a valid ObjectId string.
        try:
            ObjectId(group["_id"])
        except Exception as e:
            pytest.fail(f"_id '{group['_id']}' is not a valid ObjectId string: {e}")


def test_get_chat_groups_for_user_limit_over_total(chat_groups):
    """
    Test retrieving chat groups with a limit greater than the total number of groups.
    
    Create 3 chat groups for 'user1' and request a page with a limit of 10.
    The returned list should contain all 3 groups.
    """
    # Clear existing groups for a clean slate if needed.
    # (This depends on your test setup; if using mongomock in a fixture, the db is clean.)
    chat_groups.create_chat_group("Group A", ["user1"])
    chat_groups.create_chat_group("Group B", ["user1"])
    chat_groups.create_chat_group("Group C", ["user1"])

    results = chat_groups.get_chat_groups_for_user("user1", page=1, limit=10)
    assert len(results) == 3, "Expected to retrieve all 3 groups when limit is over the total"


def test_get_chat_groups_for_user_negative_page_limit(chat_groups):
    """Test behavior when negative or zero values are used for page or limit."""
    user_id = "test_user"

    with pytest.raises(ValueError, match="Page and limit must be greater than zero"):
        chat_groups.get_chat_groups_for_user(user_id, page=-1, limit=5)
    
    with pytest.raises(ValueError, match="Page and limit must be greater than zero"):
        chat_groups.get_chat_groups_for_user(user_id, page=1, limit=0)

    with pytest.raises(ValueError, match="Page and limit must be greater than zero"):
        chat_groups.get_chat_groups_for_user(user_id, page=0, limit=5)

    with pytest.raises(ValueError, match="Page and limit must be greater than zero"):
        chat_groups.get_chat_groups_for_user(user_id, page=2, limit=-3)