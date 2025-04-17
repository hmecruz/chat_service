from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    # Start the Flask-SocketIO server.
    socketio.run(app, host='localhost', port=5000, debug=True)

# run: python -m app.main

