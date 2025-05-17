import logging
from typing import List, Tuple

import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException

from config.xmpp_config import XMPPConfig

from .logger import xmpp_logger


class UserManagementXMPP:
    def __init__(self):
        pass

    @staticmethod
    def _post(endpoint: str, payload: dict) -> requests.Response:
        try:
            response = requests.post(
                endpoint,
                json=payload,
                auth=HTTPBasicAuth(XMPPConfig.ADMIN_USER, XMPPConfig.ADMIN_PASSWORD),
                verify=False
            )
            response.raise_for_status()
            xmpp_logger.info(f"✅ HTTP POST request to {endpoint} succeeded.")
            return response
        except RequestException as e:
            xmpp_logger.exception(f"❌ HTTP request failed (POST {endpoint}): {e}")
            raise

    @staticmethod
    def register_user(username: str, password: str):
        """Register a new user via HTTP API."""
        endpoint = f"{XMPPConfig.EJABBERD_API_URL}/register"
        payload = {
            "user": username,
            "host": XMPPConfig.VHOST,
            "password": password
        }

        try:
            UserManagementXMPP._post(endpoint, payload)
            xmpp_logger.info(f"✅ Registered user {username}@{XMPPConfig.VHOST}")
        except RequestException:
            xmpp_logger.error(f"❌ Failed to register user {username}@{XMPPConfig.VHOST}")

    @staticmethod
    def register_users(users: List[Tuple[str, str]]):
        """Register multiple users via HTTP API."""
        for username, password in users:
            UserManagementXMPP.register_user(username, password)

    @staticmethod
    def unregister_user(username: str):
        """Unregister (delete) an XMPP user from ejabberd via HTTP API."""
        endpoint = f"{XMPPConfig.EJABBERD_API_URL}/unregister"
        payload = {
            "user": username,
            "host": XMPPConfig.VHOST
        }

        try:
            UserManagementXMPP._post(endpoint, payload)
            xmpp_logger.info(f"🗑️ Unregistered user {username}@{XMPPConfig.VHOST}")
        except RequestException:
            xmpp_logger.error(f"❌ Failed to unregister user {username}@{XMPPConfig.VHOST}")

    @staticmethod
    def get_registered_users() -> List[dict]:
        """Fetch the list of registered users from ejabberd via HTTP API."""
        endpoint = f"{XMPPConfig.EJABBERD_API_URL}/registered_users"
        payload = {"host": XMPPConfig.VHOST}

        try:
            response = UserManagementXMPP._post(endpoint, payload)
            registered_users = response.json()
            xmpp_logger.info(f"✅ Retrieved registered users: {registered_users}")
            return registered_users
        except RequestException:
            xmpp_logger.error("❌ Failed to retrieve registered users")
            return []

    @staticmethod
    def ensure_users_register(users: list[str], default_password: str = "password") -> None:
        """Ensure users are registered in the XMPP server, register them if missing."""
        try:

            registered_usernames = UserManagementXMPP.get_registered_users()
            
            missing_users = [
                (user, default_password)
                for user in users
                if user not in registered_usernames
            ]

            if missing_users:
                xmpp_logger.info(f"❌ Some users are missing and will be registered: {missing_users}")
                UserManagementXMPP.register_users(missing_users)
            else:
                xmpp_logger.info(f"✅ All users are already registered: {users}")
        
        except Exception as e:
            xmpp_logger.error(f"🔥 Error ensuring user registration: {str(e)}")
            raise