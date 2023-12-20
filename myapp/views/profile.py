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



# UPDATE PROFILE
@profile_bp.route("/update_profile", methods=["POST"])
def update_profile():

    user_profile = UserProfile.query.filter_by(user_id=g.user_profile.id).first()

    # Get the new information from the request
    new_bio = request.form.get("bioVal")
    new_name = request.form.get("nameVal")
    new_age = request.form.get("ageVal")
    new_city = request.form.get("cityVal")
    new_state = request.form.get("stateVal")
    new_school = request.form.get("schoolVal")
    new_company = request.form.get("companyVal")
    new_gender = request.form.get("genderVal")
    new_sex = request.form.get("sexVal")

    if user_profile:
        # Update existing profile with new data
        if new_bio:
            user_profile.bio = new_bio
        if new_name:
            user_profile.name = new_name
        if new_age:
            user_profile.age = new_age
        if new_city:
            user_profile.city = new_city
        if new_state:
            user_profile.state = new_state
        if new_school:
            user_profile.school = new_school
        if new_company:
            user_profile.company = new_company
        if new_gender:
            user_profile.gender = new_gender
        if new_sex:
            user_profile.sex = new_sex

        db.session.commit()
        
        return "Profile data updated successfully"
    else:
        return "User profile not found"
