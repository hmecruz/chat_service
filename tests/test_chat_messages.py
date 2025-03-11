import pytest
from bson.objectid import ObjectId
from datetime import datetime

def test_store_message(chat_messages):
    """Test storing a new message in a chat."""
    chat_id = ObjectId()
    sender_id = "user123"
    content = "Hello, this is a test message."

    result = chat_messages.store_message(chat_id, sender_id, content)

    assert isinstance(result, dict)
    assert result["chat_id"] == chat_id
    assert result["sender_id"] == sender_id
    assert result["content"] == content
    assert isinstance(result["sentAt"], datetime)
    assert isinstance(result["_id"], ObjectId)

    stored_message = chat_messages.messages.find_one({"_id": result["_id"]})
    assert stored_message is not None
    assert stored_message["chat_id"] == chat_id
    assert stored_message["sender_id"] == sender_id
    assert stored_message["content"] == content
    assert stored_message["sentAt"] == result["sentAt"]
    assert isinstance(result["_id"], ObjectId)


def test_get_message(chat_messages):
    """Test retrieving a message by its ID."""

    # Insert a test message
    chat_id = ObjectId()
    message_data = chat_messages.store_message(chat_id, "user_123", "Hello, world!")

    # Retrieve the message
    retrieved_message = chat_messages.get_message(message_data["_id"])

    # Assertions
    assert retrieved_message is not None
    assert retrieved_message["_id"] == message_data["_id"]
    assert retrieved_message["chat_id"] == message_data["chat_id"]
    assert retrieved_message["sender_id"] == "user_123"
    assert retrieved_message["content"] == "Hello, world!"
    assert "sentAt" in retrieved_message


def test_get_message_not_found(chat_messages):
    """Test retrieving a message that does not exist."""
    
    non_existent_id = ObjectId()
    retrieved_message = chat_messages.get_message(non_existent_id)

    assert retrieved_message is None


def test_get_messages(chat_messages):
    """Test retrieving paginated messages for a chat group."""
    chat_id = ObjectId()

    # Insert test messages
    messages = [
        {"_id": ObjectId(), "chat_id": chat_id, "sender_id": "user1", "content": "Message 1", "sentAt": datetime.utcnow().replace(microsecond=0)},
        {"_id": ObjectId(), "chat_id": chat_id, "sender_id": "user2", "content": "Message 2", "sentAt": datetime.utcnow().replace(microsecond=0)},
    ]
    chat_messages.messages.insert_many(messages)

    result = chat_messages.get_messages(chat_id, page=1, limit=2)

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["chat_id"] == chat_id
    
    assert result[1]["chat_id"] == chat_id


def test_get_messages_no_messages(chat_messages):
    """Test that querying a chat with no messages returns an empty list."""
    chat_id = ObjectId()
    result = chat_messages.get_messages(chat_id, page=1, limit=20)
    assert isinstance(result, list)
    assert len(result) == 0


def test_get_messages_pagination(chat_messages):
    """
    Test retrieving a paginated list of messages for a given chat.
    
    This test creates 10 messages in a chat and verifies:
      - Page 1 returns 5 messages.
      - Page 2 returns 5 messages.
      - Page 3 returns an empty list.
      - Messages are sorted in descending order by "sentAt".
    """
    chat_id = ObjectId()
    total_messages = 10
    
    for i in range(total_messages):
        chat_messages.store_message(chat_id, f"Message {i+1}", "user1")
    
    page1 = chat_messages.get_messages(chat_id, page=1, limit=5)
    page2 = chat_messages.get_messages(chat_id, page=2, limit=5)
    page3 = chat_messages.get_messages(chat_id, page=3, limit=5)
    
    assert len(page1) == 5, "Page 1 should return 5 messages"
    assert len(page2) == 5, "Page 2 should return 5 messages"
    assert len(page3) == 0, "Page 3 should return 0 messages"
    
    timestamps = [msg["sentAt"] for msg in page1 + page2]
    assert timestamps == sorted(timestamps, reverse=True), "Messages should be sorted by 'sentAt' descending"


def test_get_messages_limit_over_total(chat_messages):
    """
    Test retrieving messages with a limit greater than the total number of messages.
    
    Create 3 messages in a chat and request a page with a limit of 10.
    The returned list should contain all 3 messages.
    """
    chat_id = ObjectId()
    chat_messages.store_message(chat_id, "Hello", "user1")
    chat_messages.store_message(chat_id, "How are you?", "user1")
    chat_messages.store_message(chat_id, "Goodbye", "user1")
    
    result = chat_messages.get_messages(chat_id, page=1, limit=10)
    assert len(result) == 3, "Expected to retrieve all 3 messages when limit is over the total"


def test_get_messages_invalid_chat_id(chat_messages):
    """Test querying messages with an invalid chat_id."""
    with pytest.raises(Exception):
        chat_messages.get_messages("invalid_id", page=1, limit=5)


def test_get_messages_negative_page_limit(chat_messages):
    """Test behavior when negative or zero values are used for page or limit."""
    chat_id = ObjectId()
    with pytest.raises(ValueError):
        chat_messages.get_messages(chat_id, page=-1, limit=5)
    with pytest.raises(ValueError):
        chat_messages.get_messages(chat_id, page=1, limit=0)


def test_edit_message(chat_messages):
    """Test editing an existing message."""
    message_id = ObjectId()
    chat_id = ObjectId()
    new_content = "Updated message content."

    # Insert test message
    chat_messages.messages.insert_one({"_id": message_id, "chat_id": chat_id, "sender_id": "user1", "content": "Old Content", "sentAt": datetime.utcnow().replace(microsecond=0)})

    result = chat_messages.edit_message(message_id, new_content)
    print(result)

    assert isinstance(result, dict)
    assert result["_id"] == message_id
    assert result["content"] == new_content

    updated_message = chat_messages.messages.find_one({"_id": message_id})
    print(updated_message)
    assert updated_message is not None
    assert updated_message["_id"] == message_id
    assert updated_message["chat_id"] == chat_id
    assert updated_message["sender_id"] == "user1"
    assert updated_message["content"] == new_content
    assert isinstance(updated_message["sentAt"], datetime)
    assert isinstance(updated_message["editedAt"], datetime)


def test_delete_message(chat_messages):
    """Test marking a message as deleted."""
    message_id = ObjectId()

    # Insert test message
    chat_messages.messages.insert_one({"_id": message_id, "chat_id": ObjectId(), "sender_id": "user1", "content": "Message to delete", "sentAt": datetime.utcnow().replace(microsecond=0)})

    result = chat_messages.delete_message(str(message_id))

    assert isinstance(result, int)
    assert result == 1

    deleted_message = chat_messages.messages.find_one({"_id": message_id})
    assert "deletedAt" in deleted_message