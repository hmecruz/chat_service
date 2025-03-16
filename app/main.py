# app/main.py
from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    # Start the Flask-SocketIO server.
    socketio.run(app, host='0.0.0.0', port=8080, debug=True)