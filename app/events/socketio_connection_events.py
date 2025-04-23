import jwt
from flask import request, current_app
from flask_socketio import join_room, emit, disconnect

from .logger import events_logger 

class SocketIOConnectionEvents:
    """
    Handles SocketIO connection events. Supports both JWT and plain userId-based auth.
    """

    def handle_connect(self):
        token = request.args.get('token')
        user_id = None

        # Log connection attempt
        events_logger.info(f"Connection attempt. Token provided: {bool(token)}")

        # Try JWT-based auth first
        if token:
            try:
                decoded = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
                user_id = decoded.get('sub')

                if not user_id:
                    raise ValueError("Missing user ID in token")
                
                # Log successful JWT decoding
                events_logger.info(f"User {user_id} decoded from token.")

            except jwt.ExpiredSignatureError:
                events_logger.warning("Token expired.")
                emit('error', {'type': 'unauthorized', 'message': 'Token expired'})
                disconnect()
                return
            except jwt.InvalidTokenError:
                events_logger.warning("Invalid token.")
                emit('error', {'type': 'unauthorized', 'message': 'Invalid token'})
                disconnect()
                return
            except Exception as e:
                events_logger.error(f"Error decoding token: {str(e)}")
                emit('error', {'type': 'server_error', 'message': str(e)})
                disconnect()
                return
        else:
            # Fallback to userId in query string
            user_id = request.args.get('userId')
            if not user_id:
                events_logger.warning("Missing token or userId.")
                emit('error', {'type': 'unauthorized', 'message': 'Missing token or userId'})
                disconnect()
                return

        # Log successful connection
        events_logger.info(f"User {user_id} connected successfully.")

        # Join user's personal room
        join_room(user_id)

        events_logger.debug(f"Joining room: {repr(user_id)}")

        emit('connected', {'message': f'Connected as {user_id}'})
