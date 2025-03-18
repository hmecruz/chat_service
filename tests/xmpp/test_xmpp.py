import pytest
import pytest_asyncio
from app.xmpp.chat_client import ChatClient
from app.xmpp.chat_groups_xmpp import ChatGroupsXMPP
from app.xmpp.chat_messages_xmpp import ChatMessagesXMPP

# Define XMPP credentials
XMPP_SERVER = "localhost"
USER1_JID = "user1@localhost"
USER1_PASSWORD = "password1"
USER2_JID = "user2@localhost"
USER2_PASSWORD = "password2"
ROOM_JID = "testroom@conference.localhost"
NICKNAME = "User1"

@pytest_asyncio.fixture
async def xmpp_client():
    """Fixture to set up an XMPP client for testing."""
    client = ChatClient(USER1_JID, USER1_PASSWORD)

    # Ensure the client is connected
    await client.connect()  # Fix: Directly await connect()
    
    yield client

    # Disconnect after test
    await client.disconnect()

@pytest.mark.asyncio
async def test_create_chat_group(xmpp_client):
    """Tests the creation of a chat group."""
    chat_groups = ChatGroupsXMPP(xmpp_client)
    
    # Ensure that the XMPP client is connected
    assert xmpp_client.is_connected()

    room = await chat_groups.create_chat_group(ROOM_JID, NICKNAME)
    
    # Verify the group chat room JID was returned successfully
    assert room == ROOM_JID

@pytest.mark.asyncio
async def test_send_group_message(xmpp_client):
    """Tests sending a message to a chat group."""
    chat_messages = ChatMessagesXMPP(xmpp_client)

    # Ensure the client is connected before sending messages
    assert xmpp_client.is_connected()

    await chat_messages.send_group_message(ROOM_JID, "Hello, team!")

    # No direct assertion, but you should see logs in the XMPP server