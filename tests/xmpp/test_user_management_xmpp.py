import pytest
import uuid
import requests
from requests.exceptions import HTTPError

from app.xmpp.user_management_xmpp import UserManagementXMPP


@pytest.fixture
def random_username():
    return f"testuser_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def default_password():
    return "password"


@pytest.fixture
def test_students():
    return [f"student_{uuid.uuid4().hex[:6]}" for _ in range(3)]


def test_register_user_success(random_username, default_password):
    # Should register successfully
    try:
        UserManagementXMPP.register_user(random_username, default_password)
    except HTTPError as e:
        pytest.fail(f"Registration failed unexpectedly: {e}")

    # Cleanup
    UserManagementXMPP.unregister_user(random_username)


def test_register_user_failure_duplicate(random_username, default_password):
    # Register once
    UserManagementXMPP.register_user(random_username, default_password)

    # Register again — should raise an HTTPError
    with pytest.raises(HTTPError):
        UserManagementXMPP.register_user(random_username, default_password)

    # Cleanup
    UserManagementXMPP.unregister_user(random_username)


def test_register_multiple_users(test_students, default_password):
    # Prepare user list
    users = [(student, default_password) for student in test_students]

    try:
        UserManagementXMPP.register_users(users)
    except HTTPError as e:
        pytest.fail(f"Failed to register multiple users: {e}")

    # Cleanup
    for student in test_students:
        UserManagementXMPP.unregister_user(student)


def test_unregister_user_success(random_username, default_password):
    # Register then unregister
    UserManagementXMPP.register_user(random_username, default_password)

    try:
        UserManagementXMPP.unregister_user(random_username)
    except HTTPError as e:
        pytest.fail(f"Unregistering user failed unexpectedly: {e}")


def test_get_registered_users(test_students, default_password):
    # Register users
    users = [(student, default_password) for student in test_students]
    UserManagementXMPP.register_users(users)

    # Fetch registered users
    try:
        registered = UserManagementXMPP.get_registered_users()
        for student in test_students:
            assert student in registered
    except HTTPError as e:
        pytest.fail(f"Failed to retrieve registered users: {e}")

    # Cleanup
    for student in test_students:
        UserManagementXMPP.unregister_user(student)


def test_ensure_users_register(default_password):
    base_users = [f"user_{uuid.uuid4().hex[:6]}" for _ in range(3)]

    # Ensure only missing users are registered
    try:
        UserManagementXMPP.ensure_users_register(base_users, default_password)
        registered = UserManagementXMPP.get_registered_users()
        for user in base_users:
            assert user in registered
    except HTTPError as e:
        pytest.fail(f"Failed to ensure users are registered: {e}")
    finally:
        for user in base_users:
            UserManagementXMPP.unregister_user(user)
