from flask_socketio import SocketIO

# Initialize SocketIO with the app
socketio = SocketIO(cors_allowed_origins=['http://heartsync.onrender.com/matches', 'https://heartsync.onrender.com/matches'])