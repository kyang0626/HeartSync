# MESSAGES
from flask import Blueprint, render_template, request, redirect, jsonify
from myapp import g
from flask_socketio import emit, join_room, leave_room
from ..models import Conversation, Message, UserProfile, db
from ..helpers import apology
from ..socket_init import socketio

message_bp = Blueprint("messages", __name__)

@message_bp.route("/messages", methods=["GET", "POST"])
def messages():
    profile = g.user_profile

    if request.method == "POST":

        action = request.form.get("action")

        if action == "send-message":
            chatUserId = request.form.get("chatUserId")
            print("Message user id: ", chatUserId)

            message = request.form.get("content")

            new_message = Message(sender_id=profile.id, recipient_id=chatUserId, content=message)
            db.session.add(new_message)
            db.session.commit()

            user_profile = UserProfile.query.filter_by(user_id=g.user_profile.id).first()
            recipient_profile = UserProfile.query.filter_by(user_id=chatUserId).first()

            message_content = {
                "sender": profile.id,
                "recipient": chatUserId,
                "content": message,
                "senderPic": user_profile.picture,
                "recipientPic": recipient_profile.picture
            }

            print(user_profile.picture)

            return jsonify(message_content)
        
        elif action == "display-conversation":
            
            selected_user = request.form.get("selectedUser")

            messages = Message.query.filter((Message.sender_id == selected_user) and (Message.recipient_id == selected_user))

            if messages:
                message_data = {
                    "message": message
                }
            
            return jsonify(message_data)

    else:

        sender_id = request.args.get("senderId")

        sender_profile = UserProfile.query.filter_by(user_id=sender_id).first()

        all_messages = Message.query.filter((Message.sender_id == profile.id) | (Message.recipient_id == profile.id)).all()

        user_messages = Message.query.filter((Message.sender_id == sender_id) | (Message.recipient_id == sender_id)).all()

        if user_messages:
            print("There are messages")
        else:
            print("no messages")

        participant_ids = set()
        for message in user_messages:
            participant_ids.add(message.sender_id)
            participant_ids.add(message.recipient_id)
        
        for message in all_messages:
            participant_ids.add(message.sender_id)
            participant_ids.add(message.recipient_id)

        participants = UserProfile.query.filter(UserProfile.id.in_(participant_ids) & (UserProfile.user_id != g.user_profile.id)).all()

        chat_profiles = UserProfile.query.filter(UserProfile.user_id != g.user_profile.id).all()
        
        for p in participants:
            print("participants: ", p)
            chat_profiles = UserProfile.query.filter((UserProfile.user_id != sender_id)).first()
        
        return render_template("messages.html", profile=profile, participants=participants, messages=user_messages, senderId=sender_id, senderProfile=sender_profile, allMessages=all_messages, chatProfile=chat_profiles)
    

# SocketIO event handler
@socketio.on("message")
def handle_message(data):
    senderId = data["senderId"]
    recipientId = data["recipientId"]
    message = data["message"]
    senderPic = data["senderPic"]
    recipientPic = data["recipientPic"]

    join_room(recipientId)

    print(f"Received {message} from {senderId} on server")
    emit("message", {"senderId": senderId, "recipientId": recipientId, "message": message, "senderPic": senderPic, "recipientPic": recipientPic, "room": recipientId}, room=recipientId)


@socketio.on('join_room')
def handle_join_room(data):
    room = data['room']
    join_room(room)

    print(f"User {room} has joined room {data}")
