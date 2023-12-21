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

        # Send message
        if action == "send-message":
            chatUserId = request.form.get("chatUserId")

            message = request.form.get("content")

            new_message = Message(sender_id=profile.id, recipient_id=chatUserId, content=message)
            db.session.add(new_message)
            db.session.commit()

            all_messages = Message.query.filter((Message.sender_id == profile.id) & (Message.recipient_id == chatUserId)).order_by(Message.timestamp).all()


            user_profile = UserProfile.query.filter_by(user_id=g.user_profile.id).first()
            recipient_profile = UserProfile.query.filter_by(user_id=chatUserId).first()
            print("recipient_profile", recipient_profile)

            message_content = {
                "sender": profile.id,
                "recipient": chatUserId,
                "content": message,
                "senderPic": user_profile.picture,
                "recipientPic": recipient_profile.picture
            }

            return jsonify(message_content)
        
        # Show selected user's conversation
        elif action == "display-conversation":
            selected_user = request.form.get("selectedUser")
            print("selecteduser: ", selected_user)

            selected_user_profile = UserProfile.query.filter_by(user_id=selected_user).first()

            userData = selected_user_profile.serializeUserProfile()

            messages = Message.query.filter((
                Message.sender_id == selected_user) & (Message.recipient_id == profile.id) | 
                (Message.recipient_id == selected_user) & (Message.sender_id == profile.id)).all()

            messageData = [message.serializeMessage() for message in messages]

            selected_user_data = {
                "selectedUserProfile": userData,
                "allMessages": messageData
            }

            return jsonify(selected_user_data)
        
        # Quick message from notification or match route
        elif action == "quick-message":
            chatUserId = request.form.get("chatUserId")
            print("Chat user id: ", chatUserId)

            message = request.form.get("content")

            new_message = Message(sender_id=profile.id, recipient_id=chatUserId, content=message)
            db.session.add(new_message)
            db.session.commit()

            all_messages = Message.query.filter((Message.sender_id == profile.id) & (Message.recipient_id == chatUserId)).order_by(Message.timestamp).all()


            user_profile = UserProfile.query.filter_by(user_id=g.user_profile.id).first()
            recipient_profile = UserProfile.query.filter_by(user_id=chatUserId).first()
            print("recipient_profile", recipient_profile)

            message_content = {
                "sender": profile.id,
                "recipient": chatUserId,
                "content": message,
                "senderPic": user_profile.picture,
                "recipientPic": recipient_profile.picture
            }

            return jsonify(message_content)


    else:
        sender_id = request.args.get("senderId")
        print("sender_id: ", sender_id)

        sender_profile = UserProfile.query.filter_by(user_id=sender_id).first()

        all_messages = Message.query.filter((Message.sender_id == profile.id) | (Message.recipient_id == profile.id)).all()

        participant_ids = set()        
        for message in all_messages:
            participant_ids.add(message.sender_id)
            participant_ids.add(message.recipient_id)

        participants = UserProfile.query.filter(UserProfile.id.in_(participant_ids) & (UserProfile.user_id != g.user_profile.id)).all()
   
        return render_template("messages.html", profile=profile, participants=participants, senderProfile=sender_profile, messages=all_messages)
  

# SocketIO event handler
# Listens for messages
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

# Listens for who joins the room
@socketio.on('join_room')
def handle_join_room(data):
    room = data['room']
    join_room(room)

