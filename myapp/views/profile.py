from flask import Blueprint, render_template, request
from ..models import User, UserProfile, UserInterests, NotInterested, db
from myapp import g
from flask import Blueprint, render_template

profile_bp = Blueprint("profile", __name__)

# PROFILE
@profile_bp.route("/profile")
def profile():

    profile = g.user_profile
    
    return render_template("profile.html", profile=profile)

# MESSAGES
@profile_bp.route("/edit-profile")
def edit_profile():
    user_id = g.user_id

    profile = UserProfile.query.filter_by(user_id=user_id).first()

    return render_template("edit-profile.html", profile=profile)

# UPDATE PROFILE
@profile_bp.route("/update_profile", methods=["POST"])
def update_profile():
    # Get the new information from the request
    new_info = request.form.get("new_info")

    # Update the user's profile in the database (you need to implement this)
    # ...

    # You can return a response if needed
    return "Profile updated successfully"