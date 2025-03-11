from bson.objectid import ObjectId

def test_store_message(chat_messages):
    """Test storing a message."""
    chat_id = str(ObjectId())
    message_id = chat_messages.store_message(chat_id, "user1", "Hello, World!")
    
    assert message_id is not None

    messages = chat_messages.get_messages(chat_id)
    assert len(messages) == 1
    assert messages[0]["content"] == "Hello, World!"


def test_get_messages(chat_messages):
    """Test retrieving messages with pagination."""
    chat_id = str(ObjectId())
    for i in range(10):
        chat_messages.store_message(chat_id, "user1", f"Message {i+1}")

    messages = chat_messages.get_messages(chat_id, page=1, limit=5)
    assert len(messages) == 5  # Should return only 5 messages


def test_edit_message(chat_messages):
    """Test editing a message."""
    chat_id = str(ObjectId())
    message_id = chat_messages.store_message(chat_id, "user1", "Old Message")

    chat_messages.edit_message(message_id, "New Message")
    messages = chat_messages.get_messages(chat_id)

    assert messages[0]["content"] == "New Message"
    assert "editedAt" in messages[0]


def test_delete_message(chat_messages):
    """Test deleting a message."""
    chat_id = str(ObjectId())
    message_id = chat_messages.store_message(chat_id, "user1", "To be deleted")

    chat_messages.delete_message(message_id)
    messages = chat_messages.get_messages(chat_id)

    assert "deletedAt" in messages[0]
