import requests
from requests.auth import HTTPBasicAuth

# Change these variables to suit your setup:
API_URL = "https://localhost:5443/api/register"
ADMIN_JID = "admin@localhost"
ADMIN_PASSWORD = "adminpassword"
NEW_USER = "userTest"
NEW_PASSWORD = "userTestPassword"
HOST = "localhost"  # your ejabberd virtual host

payload = {
    "user": NEW_USER,
    "host": HOST,
    "password": NEW_PASSWORD
}

response = requests.post(API_URL, json=payload,
                         #auth=HTTPBasicAuth(ADMIN_JID, ADMIN_PASSWORD),
                         verify=False)  # Set verify=True if using trusted certs

if response.status_code == 200:
    print("User registration successful.")
else:
    print("Failed to register user:", response.text)
