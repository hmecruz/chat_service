import os
from flask import Blueprint, jsonify, send_from_directory

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FRONTEND_PATH = os.path.join(BASE_DIR, '..', '..', 'chat_frontend')

static_routes_bp = Blueprint('static_routes', __name__)

@static_routes_bp.route('/')
def serve_index():
    return send_from_directory(os.path.join(FRONTEND_PATH, 'templates'), 'index.html')

@static_routes_bp.route('/assets/<path:path>')  # Use /assets instead of /static
def serve_custom_static(path):
    return send_from_directory(os.path.join(FRONTEND_PATH, 'assets'), path)

@static_routes_bp.route('/debug-test')
def debug_static_test():
    return send_from_directory(
        os.path.join(FRONTEND_PATH, 'assets', 'js'),
        'groups.js'
    )

@static_routes_bp.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(FRONTEND_PATH, 'assets', 'images'), 'default_group.png')  # or a real favicon

@static_routes_bp.route('/health')
def health():
    return jsonify(status='ok'), 200