from flask import Blueprint, render_template
from ..helpers import login_required, apology
from myapp import g
from ..models import Notification

index_bp = Blueprint("index", __name__)

@index_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    # find user profile
    profile = g.user_profile

    if profile is None:
        return apology("Profile not found")
    
    notifications = Notification.query.filter(Notification.recipient_id == g.user_profile.id).all()

    print("Index: ", notifications)

    return render_template("index.html", profile=profile, notifications=notifications)