import jwt
from flask import request, current_app
from flask_socketio import join_room, emit, disconnect

class SocketIOConnectionEvents:
    """
    Handles SocketIO connection events. Supports both JWT and plain userId-based auth.
    """

    def handle_connect(self):
        token = request.args.get('token')
        user_id = None

        # Try JWT-based auth first
        if token:
            try:
                decoded = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
                user_id = decoded.get('sub')

                if not user_id:
                    raise ValueError("Missing user ID in token")

            except jwt.ExpiredSignatureError:
                emit('error', {'type': 'unauthorized', 'message': 'Token expired'})
                disconnect()
                return
            except jwt.InvalidTokenError:
                emit('error', {'type': 'unauthorized', 'message': 'Invalid token'})
                disconnect()
                return
            except Exception as e:
                emit('error', {'type': 'server_error', 'message': str(e)})
                disconnect()
                return
        else:
            # Fallback to userId in query string
            user_id = request.args.get('userId')
            if not user_id:
                emit('error', {'type': 'unauthorized', 'message': 'Missing token or userId'})
                disconnect()
                return

        # Join user's personal room
        join_room(user_id)
        emit('connected', {'message': f'Connected as {user_id}'})
