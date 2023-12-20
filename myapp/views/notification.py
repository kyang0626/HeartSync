from flask import Blueprint, render_template, request, url_for, redirect, jsonify
from ..models import db, User, UserInterests, UserProfile, NotInterested, Conversation, Message, Notification
from ..helpers import apology
from myapp import g
from ..socket_init import socketio
from flask_socketio import emit, join_room, leave_room

notification_bp = Blueprint("notification", __name__)

@notification_bp.route("/notification", methods=["GET", "POST"])
def notification():
    if request.method == "POST":

        action = request.form.get("action")
        
        # ACCEPT 
        if action == "accept":

            sender_id = request.form.get("senderId")

            notification = request.form.get("notification")

            existing_not_interested = NotInterested.query.filter_by(user_id=g.user_profile.id).first()
            if existing_not_interested:
                db.session.delete(existing_not_interested)
                db.session.commit()
                
            try:
                # print(g.user_profile.id)
                new_interest = UserInterests(user_id=g.user_profile.id, liked_user_id=sender_id)
                db.session.add(new_interest)
                print(f"Liked {sender_id} back")

                # delete the notification after accept
                delete_notification = Notification.query.filter_by(sender_id=sender_id, recipient_id=g.user_profile.id).first()
                print(f"{delete_notification} deleted")

                if delete_notification:
                    db.session.delete(delete_notification)
                    db.session.commit()

            except Exception as e:
                print("Error inserting interests:", str(e))
                return apology("Error inserting interest")
            
            return "Success"

        # DECLINE    
        elif action == "decline":
            disliked_id = request.form.get("senderId")

            print("Not Interested: ", disliked_id)
            existing_interest = UserInterests.query.filter_by(user_id=g.user_profile.id, liked_user_id=disliked_id).first()
            if existing_interest:
                db.session.delete(existing_interest)
                db.session.commit()
        
            try:
                 # delete the notification after decline
                delete_notification = Notification.query.filter_by(sender_id=disliked_id, recipient_id=g.user_profile.id).first()
                if delete_notification:
                    db.session.delete(delete_notification)
                    db.session.commit()

                not_interested = NotInterested(user_id=g.user_profile.id, target_id=disliked_id)
                db.session.add(not_interested)

                # delete the interest from the sender after adding to not interest
                delete_sender_interest = UserInterests.query.filter_by(user_id=disliked_id, liked_user_id=g.user_profile.id).first()
                db.session.delete(delete_sender_interest)
                db.session.commit()

                return "Success"
            
            except Exception as e:
                print("Error marking as not interested:", str(e))
                return apology("Error marking as not interested")
            
    else:

        sender_id = request.args.get("senderId")
        print("Notification senderid: ", sender_id)

        sender_user_profile = UserProfile.query.filter_by(user_id=sender_id).first()
        
        return render_template("notification.html", profile=g.user_profile, senderProfile=sender_user_profile)
    
    
@socketio.on("notification")
def handle_notification(data):
    print("Notification: notification received")

    sender_id_= data["senderId"]
    recipient_id = data["recipientId"]
    notification = data["notification"]

    join_room(recipient_id)

    emit("notification", {'notification': notification, 'recipientId': recipient_id, 'senderId': sender_id_, 'room': recipient_id}, room=recipient_id)

@socketio.on('join_room')
def handle_join_room(data):
    room = data['room']
    join_room(room)