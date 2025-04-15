import logging

import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError

from config.xmpp_config import XMPPConfig


class UserManagementXMPP:
    def __init__(self):
        pass
        
    @staticmethod
    def register_user(username: str, password: str):
        """Register a new user via HTTP API."""
        endpoint = f"{XMPPConfig.EJABBERD_API_URL}/register"
        payload = {
            "user": username,
            "host": XMPPConfig.VHOST,
            "password": password
        }
        response = requests.post(
            endpoint,
            json=payload,
            auth=HTTPBasicAuth(XMPPConfig.ADMIN_USER, XMPPConfig.ADMIN_PASSWORD),
            verify=False
        )

        if response.status_code == 200:
            logging.info(f"✅ Registered user {username}@{XMPPConfig.VHOST}")
        else:
            error_message = (
                f"❌ Failed to register user {username}@{XMPPConfig.VHOST}: "
                f"Status Code: {response.status_code}, Response: {response.text}"
            )
            logging.error(error_message)
            response.raise_for_status()  # Raises requests.HTTPError

    @staticmethod
    def register_users(users: list[tuple[str, str]]):
        """Register multiple users via HTTP API."""
        for user in users:
            UserManagementXMPP.register_user(user[0], user[1])
        
    @staticmethod
    def unregister_user(username: str):
        """Unregister (delete) an XMPP user from ejabberd via HTTP API."""
        endpoint = f"{XMPPConfig.EJABBERD_API_URL}/unregister"
        payload = {
            "user": username,
            "host": XMPPConfig.VHOST
        }

        response = requests.post(
            endpoint,
            json=payload,
            auth=HTTPBasicAuth(XMPPConfig.ADMIN_USER, XMPPConfig.ADMIN_PASSWORD),
            verify=False
        )

        if response.status_code == 200:
            logging.info(f"🗑️ Unregistered user {username}@{XMPPConfig.VHOST}")
        else:
            logging.error(f"❌ Failed to unregister user {username}@{XMPPConfig.VHOST}: {response.text}")
            # WARNING: DOES NOT RAISE EXCEPTION ON ERROR FOR A NOT FOUND USER!
            response.raise_for_status()  # Raise HTTPError if status code is not 200

    @staticmethod
    def get_registered_users():
        """Fetch the list of registered users from ejabberd via HTTP API."""
        endpoint = f"{XMPPConfig.EJABBERD_API_URL}/registered_users"
        payload = {
            "host": XMPPConfig.VHOST
        }
        
        response = requests.post(
            endpoint, json=payload,
            auth=HTTPBasicAuth(XMPPConfig.ADMIN_USER, XMPPConfig.ADMIN_PASSWORD),
            verify=False
        )
        
        if response.status_code == 200:
            registered_users = response.json()
            logging.info(f"✅ Retrieved registered users: {registered_users}")
            return registered_users
        else:
            logging.error(f"❌ Failed to retrieve registered users: {response.text}")
            response.raise_for_status()  # Raise HTTPError if status code is not 200
            return []
    
    @staticmethod
    def ensure_users_register(users: list[str], default_password: str = "password") -> None:
        """Ensure users are registered in the XMPP server, register them if missing."""
        
        registered_usernames = UserManagementXMPP.get_registered_users()
        
        missing_users = [
            (user, default_password) for user in users # TODO Replace with a secure password generator
            if user not in registered_usernames
        ]

        if missing_users:
            UserManagementXMPP.register_users(missing_users)
