import os
from flask import Blueprint, send_from_directory

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
CHAT_WIDGET_PATH = os.path.join(BASE_DIR, '..', '..', 'chat-widget')

static_routes_bp = Blueprint('static_routes', __name__)

@static_routes_bp.route('/')
def serve_index():
    return send_from_directory(CHAT_WIDGET_PATH, 'index.html')

@static_routes_bp.route('/<path:path>')
def serve_static(path):
    return send_from_directory(CHAT_WIDGET_PATH, path)