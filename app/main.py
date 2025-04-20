from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    # Start the Flask-SocketIO server.
    socketio.run(
        app,
        host=app.config['HOST'],
        port=int(app.config['PORT']),
        debug=True
    )

# run: python -m app.main

