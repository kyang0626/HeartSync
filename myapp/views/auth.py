# LOGIN
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Blueprint, redirect, render_template, request, session, url_for, flash
from ..helpers import login_required, apology
from ..models import User
from myapp import db
from ..socket_init import socketio

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    # # Forget any user_id
    session.clear()
    
    if request.method == "POST":
        # Check if username was entered
        if not request.form.get("username") or not request.form.get("password"):
            return apology("Please enter username and password", 403) 
        
        # Get username and password values
        username = request.form.get("username")
        print(username)
        password = request.form.get("password")
        print(password)

        # Look for user in database
        user = User.query.filter_by(username=username).first()

        # Check if there is a user and password matches
        if user and check_password_hash(user.password_hash, password):
            # set session to the user's logging in
            session["user_id"] = user.id
            print("Session user_id: ", session.get("user_id"))
        else:
            return apology("Invalid username and/or password", 403)

        # Redirect user to matches route
        return redirect(url_for("matches.matches"))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

# LOGOUT
@auth_bp.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.pop("user_id", None)

    # Redirect user to login form
    return redirect("/")
    
# REGISTER
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # check username
        if not username or not password:
            return apology("Invalid registration information", 400)

        existing_user = User.query.filter_by(username=username).first()
        
        # Check for existing user
        if existing_user:
            return apology("User already exist!")
        
        # Check for password match
        if password != confirmation:
            return apology("Password did not match")

        # Hash password
        password_hash = generate_password_hash(
            password, method="pbkdf2:sha256:600000", salt_length=16
        )

        new_user = User(username=username, password_hash=password_hash)
        db.session.add(new_user)
        db.session.commit()
        
        return redirect("/")

    else:
        return render_template("register.html")
    

# @auth_bp.route("/register-profile", methods=["GET", "POST"])
# def register_profile(userid):

#     if request.method == "POST":
#         full_name = request.form.get("fullname")
#         city = request.form.get("city")
#         state = request.form.get("state")
#         bio = request.form.get("bio")
#         age = request.form.get("age")
#         gender = request.form.get("gender")
#         company = request.form.get("company")
#         school = request.form.get("school")
#         sexuality = request.form.get("sexuality")

        



#         return redirect("/")
    
#     else:

#         return render_template("registry-information.html")
