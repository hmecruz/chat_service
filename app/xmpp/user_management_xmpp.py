import logging

import requests
from requests.auth import HTTPBasicAuth

from config.xmpp_config import XMPPConfig


class UserManagementXMPP:
    def __init__(self, xmpp_registry):
        self.xmpp_registry = xmpp_registry

    @staticmethod
    def register_user(username: str, password: str):
        """Register a new user via HTTP API."""
        endpoint = f"{XMPPConfig.EJABBERD_API_URL}/register"
        payload = {
            "user": username, 
            "host": XMPPConfig.VHOST, 
            "password": password
            }
        response = requests.post(endpoint, json=payload,
                                auth=HTTPBasicAuth(XMPPConfig.ADMIN_USER, XMPPConfig.ADMIN_PASSWORD),
                                verify=False)
        if response.status_code == 200:
            logging.info(f"✅ Registered user {username}@{XMPPConfig.VHOST}")
        else:
            logging.error(f"❌ Failed to register user {username}@{XMPPConfig.VHOST}: {response.text}")


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
            return []
        
    def ensure_users_register(self, users: list[str]) -> None:
        """Ensure users exist in XMPP server and registry."""

        # XMPP server
        registered_users = self.get_registered_users()
        missing_users = [
            (user, password) for user, password in zip(users, "password") # Replace with actual password generation logic 
            if user not in registered_users
        ]

        if missing_users:
            self.register_users(missing_users)

        # XMPP registry
        missing_users = self.xmpp_registry.missing_users(users)
        missing_users = [
            (user, password) for user, password in zip(users, "password") # Replace with actual password generation logic 
            if user in missing_users
        ]
        self.xmpp_registry.register_users(missing_users)
