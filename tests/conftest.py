import pytest
import mongomock
from app.database.chat_groups import ChatGroups
from app.database.chat_messages import ChatMessages
from app.database.database_init import ChatServiceDatabase


class MockDatabase(ChatServiceDatabase):
    def __init__(self):
        self.client = mongomock.MongoClient()
        self.db = self.client["test_db"]

    def get_db(self):
        return self.db


@pytest.fixture
def mock_db():
    """Fixture for a mock database."""
    return MockDatabase()


@pytest.fixture
def chat_groups(mock_db):
    """Fixture for the ChatGroups DAL."""
    return ChatGroups(mock_db)


@pytest.fixture
def chat_messages(mock_db):
    """Fixture for the ChatMessages DAL."""
    return ChatMessages(mock_db)
