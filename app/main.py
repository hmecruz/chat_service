from app import create_app, register_events, socketio
from xmpp import initialize_xmpp_client

app = create_app()

with app.app_context():
    initialize_xmpp_client()

register_events()

if __name__ == '__main__':
    # Start the Flask-SocketIO server.
    socketio.run(app, host='0.0.0.0', port=8080, debug=True)