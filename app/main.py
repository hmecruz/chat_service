from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    # Start the Flask-SocketIO server.
    socketio.run(
        app,
        host=app.config['FLASK_HOST'],
        port=int(app.config['FLASK_PORT']),
        debug=True,
        allow_unsafe_werkzeug=True # For development only, not recommended for production (use eventlet instead). 
    )

# run: python -m app.main

