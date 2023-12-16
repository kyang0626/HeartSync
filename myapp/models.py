from .database import db
from datetime import datetime

# Define User model
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

class UserProfile(db.Model):
    __tablename__ = 'user_profile'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    full_name = db.Column(db.TEXT, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    city = db.Column(db.TEXT, nullable=False)
    state = db.Column(db.TEXT, nullable=False)
    picture = db.Column(db.TEXT, nullable=False)
    bio = db.Column(db.TEXT, nullable=False)
    school = db.Column(db.TEXT, nullable=False)
    company = db.Column(db.TEXT, nullable=False)
    gender = db.Column(db.TEXT, nullable=False)
    sexuality = db.Column(db.TEXT, nullable=False)
    user = db.relationship('User', backref=db.backref('profile', lazy=True))

class UserInterests(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    liked_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class NotInterested(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    target_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer)
    user2_id = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer)
    recipient_id = db.Column(db.Integer)
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer)
    recipient_id = db.Column(db.Integer)
    notification_type = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)