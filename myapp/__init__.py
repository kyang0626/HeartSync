from flask import Flask, session, g
from flask_session import Session
from .database import db
from .views.index import index_bp
from .views.auth import auth_bp
from .views.matches import matches_bp
from .views.notification import notification_bp
from .views.messages import message_bp
from .views.profile import profile_bp
from .socket_init import socketio

# Initialize app
app = Flask(__name__)

# configure app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///heartsync.db'  # SQLite database file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_NAME'] = 'user'
app.secret_key = "hello"

Session(app)

# Initialize Socket.IO with Flask
socketio.init_app(app)

#Initialize Flask-SQLAlchemy
db.init_app(app)

# Before any requests
@app.before_request
def before_request():
    from .models import UserProfile
    # identify user
    user_id = session.get('user_id')
    g.user_id = user_id

    g.user_profile = None

    if user_id is not None:
        user_profile = UserProfile.query.filter_by(user_id=g.user_id).first()
        if user_profile:
            g.user_profile = user_profile

# Route blueprints
app.register_blueprint(index_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(matches_bp)
app.register_blueprint(message_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(notification_bp)

# create context and bind application
with app.app_context():
    #create all tables in the database if they don't exist
    db.create_all()

# if __name__ == '__main__':
#     socketio.run(app, debug=True)