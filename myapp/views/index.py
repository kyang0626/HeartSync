from flask import Blueprint, render_template, jsonify
from ..helpers import login_required, apology
from myapp import g
from ..models import Notification, UserProfile

index_bp = Blueprint("index", __name__)

@index_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    # find user profile
    profile = g.user_profile

    if profile is None:
        return apology("Profile not found")

    return render_template("index.html", profile=profile)


@index_bp.route("/get-notification")
def get_notification():
    profile = g.user_profile

    notifications = Notification.query.filter_by(recipient_id=profile.id).all()

    senders_profile = UserProfile.query.join(Notification, Notification.sender_id == UserProfile.user_id).all()

    notification_data = []
    sendersInfo_data = []

    if notifications:
        for notification in notifications:
            notification_data.append({
                "senderid": notification.sender_id,
                "recipientid": notification.recipient_id,
                "notificationType": notification.notification_type
            })
    
    if senders_profile:
        for sender in senders_profile: 
            sendersInfo_data.append({
                "senderid": sender.user_id,
                "senderPic": sender.picture
            })

    response_data = {
        "notifications": notification_data,
        "senderInfo": sendersInfo_data
    }

    return jsonify(response_data)
    