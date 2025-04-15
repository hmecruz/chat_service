import pytest
import uuid
import logging
import json
import requests
from requests.exceptions import HTTPError

from app.xmpp.chat_groups_xmpp import ChatGroupsXMPP
from app.xmpp.user_management_xmpp import UserManagementXMPP
from config.xmpp_config import XMPPConfig

# --------------------------------------
# Fake Response class for monkeypatching
# --------------------------------------
class FakeResponse:
    def __init__(self, status_code, json_data=None, text=""):
        self.status_code = status_code
        self._json = json_data
        self.text = text

    def json(self):
        return self._json

    def raise_for_status(self):
        if not (200 <= self.status_code < 300):
            raise HTTPError(f"HTTP {self.status_code} Error: {self.text}")

# --------------------------------------
# Fixtures
# --------------------------------------
@pytest.fixture
def random_room():
    return f"room_{uuid.uuid4().hex[:6]}"

@pytest.fixture
def test_users():
    # Create a list of two or three test users
    return [f"user_{uuid.uuid4().hex[:6]}" for _ in range(3)]

@pytest.fixture
def default_password():
    return "password"

# Optionally, we can simulate that the UserManagement methods work as expected.
# For these tests we assume that when we call register_user it works correctly.

# --------------------------------------
# Tests for ChatGroupsXMPP methods
# --------------------------------------

def test_create_chat_group_success(random_room, test_users, monkeypatch):
    """
    Test that create_chat_group returns True when the room is created successfully.
    We simulate the /create_room_with_opts endpoint to return a JSON result of 0.
    """
    # Fake response for create_room_with_opts endpoint
    def fake_post(url, json, auth, verify):
        # Expecting POST to the /create_room_with_opts endpoint.
        if url.endswith("/create_room_with_opts"):
            return FakeResponse(200, json_data=0)
        pytest.fail("Unexpected URL in create_chat_group")
    monkeypatch.setattr(requests, "post", fake_post)

    # Ensure that our static function returns True
    result = ChatGroupsXMPP.create_chat_group(random_room, test_users)
    assert result is True

def test_create_chat_group_failure(random_room, test_users, monkeypatch):
    """
    Test that create_chat_group raises an HTTPError when the room creation returns a non-zero result.
    """
    def fake_post(url, json, auth, verify):
        if url.endswith("/create_room_with_opts"):
            # Simulate a failure: Return a JSON value that is not 0.
            return FakeResponse(200, json_data=1, text="Room creation error")
        pytest.fail("Unexpected URL in create_chat_group_failure")

    monkeypatch.setattr(requests, "post", fake_post)

    with pytest.raises(HTTPError):
        ChatGroupsXMPP.create_room_with_opts(random_room, options=[])

def test_delete_chat_group_success(random_room, monkeypatch):
    """
    Test that delete_chat_group returns True on successful deletion.
    """
    def fake_post(url, json, auth, verify):
        if url.endswith("/destroy_room"):
            return FakeResponse(200)
        pytest.fail("Unexpected URL in delete_chat_group")
    monkeypatch.setattr(requests, "post", fake_post)

    result = ChatGroupsXMPP.delete_chat_group(random_room)
    assert result is True

def test_delete_chat_group_failure(random_room, monkeypatch):
    """
    Test that delete_chat_group raises an HTTPError when deletion fails.
    """
    def fake_post(url, json, auth, verify):
        if url.endswith("/destroy_room"):
            return FakeResponse(400, text="Bad Request")
        pytest.fail("Unexpected URL in test_delete_chat_group_failure")
    monkeypatch.setattr(requests, "post", fake_post)

    with pytest.raises(HTTPError):
        ChatGroupsXMPP.delete_chat_group(random_room)

def test_get_user_rooms_success(monkeypatch):
    """
    Test that get_user_rooms returns a list of rooms when successful.
    """
    fake_rooms = ["room1@conference.example.com", "room2@conference.example.com"]
    
    def fake_post(url, json, auth, verify):
        if url.endswith("/get_user_rooms"):
            return FakeResponse(200, json_data=fake_rooms)
        pytest.fail("Unexpected URL in get_user_rooms")
    monkeypatch.setattr(requests, "post", fake_post)

    rooms = ChatGroupsXMPP.get_user_rooms("alice")
    assert rooms == fake_rooms

def test_get_room_occupants_success(monkeypatch):
    """
    Test that get_room_occupants returns a list of occupant dictionaries.
    """
    fake_occupants = [
        {"jid": "user1@example.com/psi", "nick": "User1", "role": "owner"},
        {"jid": "user2@example.com/psi", "nick": "User2", "role": "member"}
    ]
    
    def fake_post(url, json, auth, verify):
        if url.endswith("/get_room_occupants"):
            return FakeResponse(200, json_data=fake_occupants)
        pytest.fail("Unexpected URL in get_room_occupants")
    monkeypatch.setattr(requests, "post", fake_post)

    occupants = ChatGroupsXMPP.get_room_occupants("room1")
    assert occupants == fake_occupants

def test_set_room_affiliation_failure(monkeypatch):
    """
    Test that set_room_affiliation raises an HTTPError on failure.
    """
    def fake_post(url, json, auth, verify):
        if url.endswith("/set_room_affiliation"):
            # Simulate success HTTP code but non-zero JSON result
            return FakeResponse(200, json_data=1, text="Affiliation error")
        pytest.fail("Unexpected URL in set_room_affiliation_failure")

    monkeypatch.setattr(requests, "post", fake_post)

    with pytest.raises(HTTPError):
        ChatGroupsXMPP.set_room_affiliation("room123", "user456", "member")

def test_set_room_affiliation_failure(monkeypatch):
    """
    Test that set_room_affiliation raises an HTTPError on failure.
    """
    def fake_post(url, json, auth, verify):
        if url.endswith("/set_room_affiliation"):
            # Simulate success HTTP code but nonzero JSON result
            return FakeResponse(200, json_data=1, text="Affiliation error")
        pytest.fail("Unexpected URL in set_room_affiliation_failure")
    monkeypatch.setattr(requests, "post", fake_post)

    with pytest.raises(HTTPError):
        ChatGroupsXMPP.set_room_affiliation("room1", "bob", "member")

def test_add_and_remove_users(monkeypatch):
    """
    Test adding and removing multiple users using the corresponding methods.
    """
    # Use the fake set_room_affiliation so that it returns True
    def fake_set_room_affiliation(room, user, affiliation):
        return True
    monkeypatch.setattr(ChatGroupsXMPP, "set_room_affiliation", staticmethod(fake_set_room_affiliation))

    # Test adding users to room
    add_result = ChatGroupsXMPP.add_users_to_room("room1", ["alice", "bob"])
    assert add_result is True

    # Test removing users from room
    remove_result = ChatGroupsXMPP.remove_users_from_room("room1", ["alice", "bob"])
    assert remove_result is True

# Optional cleanup if desired: Could also use UserManagementXMPP.unregister_user for real integration.
