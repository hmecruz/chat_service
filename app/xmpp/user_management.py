import logging

import requests
from requests.auth import HTTPBasicAuth

from config.xmpp_config import XMPPConfig


class UserManagement:

    def __init__(self):
        pass

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


    def unregister_user(self, username: str):
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
