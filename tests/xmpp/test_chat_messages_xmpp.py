import pytest
import uuid
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError

from app.xmpp.chat_messages_xmpp import ChatMessagesXMPP
from config.xmpp_config import XMPPConfig

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
        # 👇 Added this for test to trigger HTTPError when response JSON != 0
        if self._json and self._json != 0:
            raise HTTPError(f"API responded with error code: {self._json}")

@pytest.fixture
def test_users():
    return [f"user_{uuid.uuid4().hex[:6]}" for _ in range(2)]

@pytest.fixture
def random_room():
    return f"testroommsg_{uuid.uuid4().hex[:6]}"

def test_send_groupchat_message_success(monkeypatch, random_room, test_users):
    sender = test_users[0]
    group_jid = f"{random_room}@{XMPPConfig.MUC_SERVICE}"

    def fake_post(url, json, auth, verify):
        if url.endswith("/send_message"):
            assert json["type"] == "groupchat"
            assert json["from"] == f"{sender}@{XMPPConfig.VHOST}"
            assert json["to"] == group_jid
            assert json["body"] == "Hi everyone"
            return FakeResponse(200, json_data=0)
        pytest.fail("Unexpected URL in send_groupchat_message")

    monkeypatch.setattr(requests, "post", fake_post)

    result = ChatMessagesXMPP.send_message(
        sender,
        random_room,  # room name only; domain added inside the function
        "groupchat",
        "",
        "Hi everyone"
    )
    assert result is True

def test_send_message_failure(monkeypatch):
    def fake_post(url, json, auth, verify):
        if url.endswith("/send_message"):
            return FakeResponse(200, json_data=1, text="Message failed")
        pytest.fail("Unexpected URL in send_message_failure")

    monkeypatch.setattr(requests, "post", fake_post)

    with pytest.raises(HTTPError):
        ChatMessagesXMPP.send_message("user1", "user2", "chat", "", "Hello")
