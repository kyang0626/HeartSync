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

            # Check if user is already in NotInterested
            existing_not_interested = NotInterested.query.filter_by(user_id=g.user_profile.id, target_id=liked_id).first()
            if existing_not_interested:
                db.session.delete(existing_not_interested)
                db.session.commit()

            try:
                # Add interest
                new_interest = UserInterests(user_id=g.user_profile.id, liked_user_id=liked_id)
                db.session.add(new_interest)
                # Send user notification
                new_notification = Notification(sender_id=g.user_profile.id, recipient_id=liked_id, notification_type=notification)
                db.session.add(new_notification)
                db.session.commit()

                # Find selected user 
                selected_user = UserProfile.query.filter(UserProfile.user_id == liked_id).first()

                if selected_user:
                    user_data = {"userid": selected_user.user_id, 
                                 "fullname": selected_user.full_name, 
                                "picture": selected_user.picture, 
                                "age": selected_user.age, 
                                "city": selected_user.city, 
                                "state": selected_user.state,
                                "school": selected_user.school, 
                                "company": selected_user.company
                                
                                }

                # return json data to display the add to left panel (matches)
                return jsonify(user_data)
                
            except Exception as e:
                print("Error inserting interests:", str(e))
                return apology("Error inserting interest")
        
        # If user is not interested
        elif action == "not-interested":
            disliked_id = request.form.get("user_id")
            print("Not Interested: ", disliked_id)
            # look for interest user in interested
            existing_interest = UserInterests.query.filter_by(user_id=g.user_profile.id, liked_user_id=disliked_id).first()
            if existing_interest:
                db.session.delete(existing_interest)
                db.session.commit()
        
            try:
                # Add non-interest to not interested table
                not_interested = NotInterested(user_id=g.user_profile.id, target_id=disliked_id)
                db.session.add(not_interested)
                db.session.commit()
                return "Success"
            except Exception as e:
                print("Error marking as not interested:", str(e))
                return apology("Error marking as not interested")

        # show selected user's profile when clicked
        elif action == "display-user":
            selected_id = request.form.get("selectedUser")

            likeBackIsTrue = False

            # check if the selected user has liked back
            selected_like_back = UserInterests.query.filter(UserInterests.user_id == selected_id, UserInterests.liked_user_id == profile.id).first()
            print("selected like back: ", selected_like_back)

            if selected_like_back:
                likeBackIsTrue = True
            
            if selected_id:
                print("selected id: ", selected_id)

                # Find selected profile to display on the right panel
                selected_user = UserProfile.query.filter_by(user_id=selected_id).first()

                print("like back: ", likeBackIsTrue)

                if selected_user:

                    user_data = {"userid": selected_user.user_id, 
                                 "fullname": selected_user.full_name, 
                                "picture": selected_user.picture, 
                                "age": selected_user.age, 
                                "city": selected_user.city, 
                                "state": selected_user.state,
                                "school": selected_user.school, 
                                "company": selected_user.company,
                                "likeBack": likeBackIsTrue
                                }
                    
                    # return json data of selected user to display
                    return jsonify(user_data)
                
                else:
                    abort(404)

            else:
                return jsonify({"error": "No selected user id"})

        elif action == "show-sender-notification":
            sender_id = request.form.get("senderId")

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
        # Get a random profile to display
        random_user = get_random_user(profile)
        print(random_user)

        # Other users' profile
        interested_profiles = get_interested_profiles(profile)

        # User's notifications
        notifications = Notification.query.filter(Notification.recipient_id == g.user_profile.id).all()

        #check if both users are interested in each other

        return render_template("matches.html", profile=profile, match=random_user,
                                interests=interested_profiles, notification=notifications)

def get_random_user(profile):
    interests_ids = [record.liked_user_id for record in UserInterests.query.filter_by(user_id=g.user_profile.id).all()]
    not_interested_ids = [record.target_id for record in NotInterested.query.filter_by(user_id=g.user_profile.id).all()]

    users_query = UserProfile.query.filter(UserProfile.user_id != profile.id)

    if profile.sexuality == "heterosexual":
        users_query = users_query.filter(UserProfile.gender != profile.gender)
    elif profile.sexuality == "homosexual":
        users_query = users_query.filter(UserProfile.gender == profile.gender)

    users_profile = users_query.filter(
        ~UserProfile.user_id.in_(interests_ids) & ~UserProfile.user_id.in_(not_interested_ids)
    ).all()

    if not users_profile:
        abort(404)
    
    random_profile = random.choice(users_profile)
    return {"userid": random_profile.user_id, 
        "fullname": random_profile.full_name, 
        "picture": random_profile.picture, 
        "age": random_profile.age, 
        "city": random_profile.city, 
        "state": random_profile.state,
        "school": random_profile.school, 
        "company": random_profile.company

    }

@matches_bp.route("/matches/next-user", methods=["GET"])
def get_next_user():
    print("working")

    current_user_id = request.args.get("currentUserId")

    current_user_profile = UserProfile.query.filter_by(user_id=current_user_id).first()

    if current_user_profile.sexuality == "heterosexual":
        users_profile = UserProfile.query.filter((UserProfile.user_id != current_user_id) & (UserProfile.gender != current_user_profile.gender))
    elif current_user_profile.sexuality == "homosexual":
        users_profile = UserProfile.query.filter((UserProfile.user_id != current_user_id) & (UserProfile.gender == current_user_profile.gender))
    else:
        users_profile = UserProfile.query.filter(UserProfile.user_id != current_user_id)

    interests_ids = [record.liked_user_id for record in UserInterests.query.filter_by(user_id=current_user_id).all()]
    not_interested_ids = [record.target_id for record in NotInterested.query.filter_by(user_id=current_user_id).all()]

    users_profile = users_profile.filter(~UserProfile.user_id.in_(interests_ids) & ~UserProfile.user_id.in_(not_interested_ids))

    if not users_profile:
        abort(404)
    
    users_profile_list = list(users_profile)

    random_profile = random.choice(users_profile_list)
    print(random_profile)

    print("Random profile: ", random_profile)

    if random_profile:
        random_user_data = { "userid": random_profile.user_id,
                            "fullname": random_profile.full_name,
                            "picture": random_profile.picture,
                            "age": random_profile.age,
                            "city": random_profile.city,
                            "state": random_profile.state,
                            "school": random_profile.school,
                            "company": random_profile.company
                            }
        return jsonify(random_user_data)
    else:
        return jsonify({"error": "No random user found"})
            
def get_interested_profiles(profile):
    return UserProfile.query.join(UserInterests, UserProfile.user_id == UserInterests.liked_user_id).filter(
        UserInterests.user_id == profile.id
    ).all()

    
# SocketIO notification event handler
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

