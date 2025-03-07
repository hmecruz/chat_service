import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "your_default_secret_key")  # Security key for sessions
    DEBUG = os.getenv("DEBUG", "True") == "True"  # Enable/Disable debug mode
    CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "*")  # Control allowed origins for WebSocket
    SOCKETIO_MESSAGE_QUEUE = os.getenv("SOCKETIO_MESSAGE_QUEUE", None)  # Use Redis or another broker if needed