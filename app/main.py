from flask import Flask
from flask_socketio import SocketIO

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')  # Load configurations
    socketio.init_app(app, cors_allowed_origins='*')
    return app

socketio = SocketIO()

if __name__ == "__main__":
    app = create_app()
    socketio.run(app, debug=True)
