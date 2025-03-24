import os
import requests

from cs50 import SQL
from flask import Flask, flash, get_flashed_messages, redirect, render_template, request, session, jsonify
from flask_session import Session
from numpy import full
#from sphinx import ret
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///messaging.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        fullname = request.form.get("fullname")
        country = request.form.get("country")
        password = request.form.get("password")
        passwordconf = request.form.get("confirmation")
        if not fullname:  # check if no fullname provided
            return apology("Please provide Full Name", 400)
        if not username:  # check of no username entered in form
            return apology("Please provide username", 400)
        if not password:  # check if no password provided
            return apology("Please provide password", 400)
        if not passwordconf:  # check if password confirm provided
            return apology("Please Confirm password", 400)
        if password != passwordconf:  # check if password matches confirmation
            return apology("Passwords must match", 400)
        if not country:  # check if no country provided
            return apology("Please provide country", 400)
        try:  # Attempt to insert user
            # inset username with hashed password
            db.execute("INSERT INTO users (username, hash, full_name, country) VALUES (?,?,?,?)",
                       username, generate_password_hash(password), fullname, country)
            # Retrieve the user_id after inserting the user
            user_id = db.execute("SELECT id FROM users WHERE username = ?", username)[0]["id"]
            session["user_id"] = user_id
            flash("Registered Successfully!")  # Store the message in the reg session
            return redirect("/")  # if success, redirect to login
        except ValueError:  # If SQL returns Error, return apology
            return apology("Sorry, user already exists, please try again", 400)
    return render_template("register.html")

@app.route("/")
@login_required
def index():
    """Index page"""
    user_id = session["user_id"]  # User ID for SQL query
    messages = get_flashed_messages(with_categories=False)  # flash messages for actions
    greet  = db.execute("SELECT full_name FROM users WHERE id = ?", user_id)[0]["full_name"]
    in_messages = db.execute("SELECT COUNT(*) FROM messages WHERE receiver_id = ? AND status = 'sent'", user_id)[0]["COUNT(*)"]
    pending_requests = db.execute("SELECT COUNT(*) FROM friends WHERE addressee_id = ? AND status = 'pending'", user_id)[0]["COUNT(*)"]
    return render_template("index.html", greet=greet, in_messages=in_messages, pending_requests=pending_requests)


@app.route("/friends", methods=["GET", "POST"])
@login_required
def buy():
    """Show friends"""
    user_id = session["user_id"]  # User ID for SQL query
    friends = db.execute("SELECT u.id, u.full_name, u.country FROM friends f JOIN users u ON u.id = f.addressee_id WHERE f.requester_id = ? AND f.status = 'accepted' UNION SELECT u.id, u.full_name, u.country FROM friends f JOIN users u ON u.id = f.requester_id WHERE f.addressee_id = ? AND f.status = 'accepted';", user_id, user_id)
    if request.method == "POST":
        return render_template("send.html")
    return render_template("friends.html", friends=friends)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

# Search for friends by name
@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    """Search for friends"""
    if request.method == "POST":
        friend_name = request.form.get("friend")
        if not friend_name:
            return apology("Please provide a friend name", 400)
        # Query database for friend name
        friends = db.execute("SELECT id, username, full_name, country FROM users WHERE full_name LIKE ?", "%" + friend_name + "%")
        if len(friends) < 1:
            return apology("Friend not found", 400)
        return render_template("search.html", friends=friends)
    return render_template("search.html")

# Allow sending friend requests from Friends page
@app.route("/request", methods=["GET", "POST"])
@login_required
def requests():
    requester_id = session["user_id"]  # User ID for SQL query
    
    """send friend request"""
    if request.method == "POST":
        addressee_id = request.form.get("friend_id")
        if not addressee_id:
            return apology("Please provide a friend name", 400)
        addressee_id = int(addressee_id) # convert str to int for DB insert
        if addressee_id == requester_id: # prevent self friending
                  return apology("You cannot friend yourself, silly 🤣", 400)
        
        # check if request already exists
        existing = db.execute(
            "SELECT * FROM friends WHERE requester_id = ? AND addressee_id = ?",
            requester_id, addressee_id)
        if existing:
            return apology("Friend request already sent or you’re already friends", 400)
        
        #insert friend request into DB
        db.execute(
            "INSERT INTO friends (requester_id, addressee_id, status) VALUES (?, ?, ?)",
            requester_id, addressee_id, "pending")
        
        flash("Friend request sent!")
        return redirect("/requests")
    else:
        return render_template("index.html")

# Check friend requests    
@app.route("/requests")
@login_required
def check_requests():
    """Check for friend requests"""
    addressee_id = session["user_id"]  # The logged-in user receiving requests
    requests = db.execute("SELECT u.username, u.country, u.full_name, f.requester_id, f.request_date FROM friends f JOIN users u ON u.id = f.requester_id WHERE f.addressee_id = ? AND f.status = 'pending'", addressee_id)
    sent_requests = db.execute("SELECT u.username, u.country, u.full_name, f.addressee_id, f.status, f.request_date FROM friends f JOIN users u ON u.id = f.addressee_id WHERE f.requester_id = ? ORDER BY f.request_date DESC", addressee_id)
    return render_template("requests.html", requests=requests,  sent_requests=sent_requests)

# Accept a friend request
@app.route("/accept", methods=["POST"])
@login_required
def accept():
    user_id = session["user_id"]
    requester_id = request.form.get("requester_id")
    db.execute(
        "UPDATE friends SET status = 'accepted' WHERE requester_id = ? AND addressee_id = ?", requester_id, user_id)
    flash("Friend request accepted!")
    return redirect("/requests")

# Reject a friend request
@app.route("/reject", methods=["POST"])
@login_required
def reject():
    user_id = session["user_id"]
    requester_id = request.form.get("requester_id")
    db.execute(
        "UPDATE friends SET status = 'rejected' WHERE requester_id = ? AND addressee_id = ?", requester_id, user_id)
    flash("Friend request rejected!")
    return redirect("/requests")

## A page for sending messages to friends
@app.route("/send", methods=["GET", "POST"])
@login_required
def send():
    friend_id = request.form.get("friend_id")
    if request.method == "POST":
        friend_info = db.execute("SELECT * FROM users WHERE id = ?", friend_id)
        if not friend_info:
            flash("Invalid friend ID!")
        return render_template("send.html", friend_info=friend_info)
    else:
        return render_template("send.html")


# A route for delete message action
@app.route("/delete", methods=["POST"])
@login_required
def delete_message():
    message_id = request.form.get("message_id")
    print("MESSAGEID:",message_id)
    # Set Message status to trash
    db.execute("UPDATE messages SET status = 'trash'  WHERE id = ?", message_id)
    flash("Message deleted!")
    return redirect("/inbox")
    
    
# Send message to a friend 
@app.route("/send_message", methods=["POST"])
@login_required
def send_message():
    user_id = session["user_id"]
    recipient_id = request.form.get("recipient_id")
    message = request.form.get("message")
    db.execute("INSERT INTO messages (sender_id, receiver_id, content, status) VALUES (?, ?, ?, 'sent')", 
               user_id, recipient_id, message)
    flash("Message sent!")
    return redirect("/inbox")

# Inbox page
@app.route("/inbox", methods=["GET", "POST"])
@login_required
def inbox():
    """ Show messages sent and received by user """
    # Collect transaction data for user
    user_id = session["user_id"]  # User ID for SQL query
    in_messages = db.execute("SELECT m.id, m.sender_id, m.content, m.timestamp, u.full_name, m.is_read FROM messages m JOIN users u ON u.id = m.sender_id WHERE m.receiver_id = ? AND m.status = 'sent' ORDER BY m.timestamp DESC;", user_id)
    out_messages = db.execute("SELECT m.id, m.content, m.timestamp, u.full_name, m.is_read FROM messages m JOIN users u ON u.id = m.receiver_id WHERE m.sender_id = ? AND m.status = 'sent' ORDER BY m.timestamp DESC;", user_id)
    return render_template("inbox.html", in_messages=in_messages, out_messages=out_messages)

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/history")
@login_required
def history():
    """Show messages sent and received by user"""
    # Collect transaction data for user
    user_id = session["user_id"]  # User ID for SQL query
    return render_template("history.html")