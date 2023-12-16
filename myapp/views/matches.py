import random

from flask import Blueprint, render_template, request, url_for, redirect, jsonify, abort
from ..models import db, User, UserInterests, UserProfile, NotInterested, Conversation, Message, Notification
from myapp import g
from ..socket_init import socketio
from flask_socketio import emit, SocketIO, join_room, leave_room
from ..helpers import apology

matches_bp = Blueprint("matches", __name__)

@matches_bp.route("/matches", methods=["GET", "POST"])
def matches():
    profile = g.user_profile

    if profile is None:
        return apology("None")

    #**Select all users for now
    if request.method == "POST":
        action = request.form.get("action")

        # INTERESTED
        if action == "interested":
            liked_id = request.form.get("user_id")
            notification = request.form.get("notification")
            print("You like: ", liked_id)
            # print("Notification type post: ", notification)

            existing_not_interested = NotInterested.query.filter_by(user_id=g.user_profile.id, target_id=liked_id).first()
            if existing_not_interested:
                db.session.delete(existing_not_interested)
                db.session.commit()

            try:
                new_interest = UserInterests(user_id=g.user_profile.id, liked_user_id=liked_id)
                db.session.add(new_interest)
                new_notification = Notification(sender_id=g.user_profile.id, recipient_id=liked_id, notification_type=notification)
                db.session.add(new_notification)
                db.session.commit()

                selected_user = UserProfile.query.filter(UserProfile.user_id == liked_id).first()

                if selected_user:
                    user_data = {"userid": selected_user.user_id, 
                                 "fullname": selected_user.full_name, 
                                "picture": selected_user.picture, 
                                "age": selected_user.age, 
                                "city": selected_user.city, 
                                "state": selected_user.state,
                                "school": selected_user.school, 
                                "company": selected_user.company}

                return jsonify(user_data)
                
            
            except Exception as e:
                print("Error inserting interests:", str(e))
                return apology("Error inserting interest")
        
        elif action == "not-interested":
            disliked_id = request.form.get("user_id")
            print("Not Interested: ", disliked_id)
            existing_interest = UserInterests.query.filter_by(user_id=g.user_profile.id, liked_user_id=disliked_id).first()
            if existing_interest:
                db.session.delete(existing_interest)
                db.session.commit()
        
            try:
                not_interested = NotInterested(user_id=g.user_profile.id, target_id=disliked_id)
                db.session.add(not_interested)
                db.session.commit()
                return "Success"
            except Exception as e:
                print("Error marking as not interested:", str(e))
                return apology("Error marking as not interested")

        elif action == "display-user":
            selected_id = request.form.get("selectedUser")
            # interest_pic = request.form.get("interest_pic")
            print("next button clicked!")
            
            if selected_id:
                print("selected id: ", selected_id)
                selected_user = UserProfile.query.filter_by(user_id=selected_id).first()

                if selected_user:

                    user_data = {"userid": selected_user.user_id, 
                                 "fullname": selected_user.full_name, 
                                "picture": selected_user.picture, 
                                "age": selected_user.age, 
                                "city": selected_user.city, 
                                "state": selected_user.state,
                                "school": selected_user.school, 
                                "company": selected_user.company}
                
                    return jsonify(user_data)
                else:
                    abort(404)

            else:
                return jsonify({"error": "No selected user id"})
        
        elif action == "next-user":

            current_userId = request.form.get("currentUserId")

            current_user_profile = UserProfile.query.filter_by(user_id=current_userId).first()

            if current_user_profile.sexuality == "heterosexual":
                users_profile = UserProfile.query.filter((UserProfile.user_id != current_userId) & (UserProfile.gender != current_user_profile.gender)).all()
            elif current_user_profile.sexuality == "homosexual":
                users_profile = UserProfile.query.filter((UserProfile.user_id != current_userId) & (UserProfile.gender == current_user_profile.gender)).all()
            else:
                users_profile = UserProfile.query.filter(UserProfile.user_id != current_userId).all()
            
            interests_ids = [record.liked_user_id for record in UserInterests.query.filter_by(user_id=current_userId).all()]
            not_interested_ids = [record.target_id for record in NotInterested.query.filter_by(user_id=current_userId).all()]

            users_profile = [user for user in users_profile if user.user_id not in interests_ids and user.user_id not in not_interested_ids]

            if not users_profile:
                abort(404)

            random_profile = random.choice(users_profile)
            print("random_profile: ", random_profile)

            if random_profile:
                random_user_data = {"userid": random_profile.user_id, 
                                    "fullname": random_profile.full_name, 
                                    "picture": random_profile.picture, 
                                    "age": random_profile.age, 
                                    "city": random_profile.city, 
                                    "state": random_profile.state,
                                    "school": random_profile.school, 
                                    "company": random_profile.company
                                    }
                return jsonify(random_user_data)


        elif action == "show-sender-notification":

            sender_id = request.form.get("senderId")
            print("senderid: ", sender_id)

            sender_profile = UserProfile.query.filter_by(user_id=sender_id).first()

            if sender_profile:

                user_data = {
                    "userid": sender_id,
                    "name": sender_profile.full_name,
                    "age": sender_profile.age,
                    "city": sender_profile.city,
                    "state": sender_profile.state
                }

            return jsonify(user_data)

    else:

        interests_ids = [record.liked_user_id for record in UserInterests.query.filter_by(user_id=g.user_profile.id).all()]
        not_interested_ids = [record.target_id for record in NotInterested.query.filter_by(user_id=g.user_profile.id).all()]

        if profile.sexuality == "heterosexual":
            #  print("heterosexual")
             other_profiles = UserProfile.query.filter(
            (UserProfile.user_id != g.user_id) &
            (UserProfile.gender != profile.gender) &
            ~UserProfile.user_id.in_(interests_ids) & 
            ~UserProfile.user_id.in_(not_interested_ids)
            ).all()
        
        elif profile.sexuality == "homosexual":
            # print("homosexual")
            other_profiles = UserProfile.query.filter(
            (UserProfile.user_id != g.user_id) &
            ~UserProfile.user_id.in_(interests_ids) & 
            ~UserProfile.user_id.in_(not_interested_ids)
            ).all()      
       
        random_index = random.randint(0, len(other_profiles) - 1)
        random_profile = other_profiles[random_index]

        interested_profiles = UserProfile.query.join(UserInterests, UserProfile.user_id == UserInterests.liked_user_id).filter(UserInterests.user_id == g.user_profile.id).all()

        print("random profile:", random_profile.full_name)

        notifications = Notification.query.filter(Notification.recipient_id == g.user_profile.id).all()

        selected_id = None
            # interest_pic = request.form.get("interest_pic")
            
        if selected_id:
            print("selected id: ", selected_id)
            
        selected_user = UserProfile.query.filter_by(user_id = selected_id).first()
        # print("selected profile: ", selected_user.full_name)

        return render_template("matches.html", profile=profile, match=random_profile, interests=interested_profiles, notifications=notifications, selectedUser=selected_user)

notification_bp = Blueprint("notification", __name__)
    
# SocketIO event handler
@socketio.on("notification")
def handle_notification(data):
    print("Server side: received notification")
    sender_id_= data["senderId"]
    recipient_id = data["recipientId"]
    notification = data["notification"]

    join_room(recipient_id)

    emit("notification", {'notification': notification, 'recipientId': recipient_id, 'senderId': sender_id_, 'room': recipient_id}, room=recipient_id)

@socketio.on('join_room')
def handle_join_room(data):
    room = data['room']
    join_room(room)

