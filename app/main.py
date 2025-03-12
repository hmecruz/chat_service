from dotenv import load_dotenv
from flask import Flask
from flask_socketio import SocketIO
from database.chat_groups import ChatGroups
from database.chat_messages import ChatMessages
from database.database_init import ChatServiceDatabase

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')  # Load configurations
    socketio.init_app(app, cors_allowed_origins='*')
    return app

socketio = SocketIO()

if __name__ == "__main__":
    load_dotenv()
    app = create_app()
    socketio.run(app, debug=True)

    db_instance = ChatServiceDatabase()
    chat_groups = ChatGroups(db_instance.get_database())
    chat_messages = ChatMessages(db_instance.get_database())
    

