import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from functools import wraps
import uuid
#from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

# Configure application
app = Flask(__name__)

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["expires"] = 0
    response.headers["pragma"] = "no-cache"
    return response

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Decorate routes to ensure user is logged in
def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")

# Lists of user specific data to be used
shop_items_list = db.execute("SELECT id FROM shop_items;")
shop_items = []
for i in shop_items_list:
    shop_items.append(i["id"])
collectable_types_list = db.execute("SELECT id FROM collectable_types;")
collectable_types = []
for i in collectable_types_list:
    collectable_types.append(i["id"])

# Initialise user specific shop item and collectable data
def newAccountHandler(userID):
    for i in shop_items:
        db.execute("INSERT INTO user_items (user_id, item_id) VALUES(?, ?);", userID, i)
    for i in collectable_types:
        db.execute("INSERT INTO user_collectables (user_id, collectable_id) VALUES(?, ?);", userID, i)


@app.route("/")
def index():
    return render_template("index.html")

# Handle user log in
@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Check if request was sent from account login form
        if len(request.form) > 0:

            # Ensure username was submitted
            if not request.form.get("username"):
                return render_template("login.html", message="Must provide username!")

            # Ensure password was submitted
            if not request.form.get("password"):
                return render_template("login.html", message="Must provide password!")

            # Query database for username
            accounts = db.execute("SELECT * FROM users WHERE username = ?;", request.form.get("username"))

            # Ensure username exists and password is correct
            if len(accounts) != 1 or not check_password_hash(accounts[0]["hash"], request.form.get("password")):
                return render_template("login.html", message="Invalid username and/or password!")

            # Remember which user has logged in
            session["user_id"] = accounts[0]["id"]

            """ Test Code

            # Load user specific data into session
            levels = db.execute("SELECT level FROM user_items WHERE user_id = ?;", session["user_id"])
            collectables = db.execute("SELECT amount FROM user_collectables WHERE user_id = ?;", session["user_id"])
            session["user_items"] = {}
            session["user_collectables"] = {}
            for i in range(len(shop_items)):
                session["user_items"][shop_items[i]] = levels[i]
            for i in range(len(collectable_types)):
                session["user_collectables"][collectable_types[i]] = collectables[i]

            """

        # When request comes from guest login form
        else:
            # Generate a unique username
            username = uuid.uuid4().int
            while (db.execute("SELECT id FROM users WHERE username = ?;", username)):
                username = uuid.uuid4().int
            session["user_id"] = username

            # Store user specific values in session
            session["user_items"] = {}
            session["user_collectables"] = {}
            for i in shop_items:
                session["user_items"][i] = 0
            for i in collectable_types:
                session["user_collectables"][i] = 100

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    # Register the user with a username and password

    if request.method == "POST":

        username = request.form.get('username')
        password = request.form.get('password')
        confirmation = request.form.get('confirm_password')

        # No username entered
        if not username:
            return render_template("register.html", message="Must provide username!")

        # Username and password cannot have a space
        if ' ' in username or ' ' in password:
            return render_template("register.html", message="No spaces are allowed in username and password")

        account = db.execute('SELECT * FROM users WHERE username = ?;', request.form.get('username'))
        # Username already exists
        if len(account):
            return render_template("register.html", message="Username already exists!")

        # No password entered
        if not password:
            return render_template("register.html", savedUsername=username, message="Must provide password!")

        # Password must contain capital letters, lower case letters, numbers and symbols without any spaces
        upper, lower, numbers, symbols = 0, 0, 0, 0
        for char in password:
            if char == " ":
                return render_template("register.html", savedUsername=username, message="Password must not contain a space!")

            # counting number of upper and lower case letters, numbers and symbols
            if 65 <= ord(char) <= 90:
                upper += 1
            elif 97 <= ord(char) <= 122:
                lower += 1
            elif 48 <= ord(char) <= 57:
                numbers += 1
            elif 33 <= ord(char) <= 47 or 58 <= ord(char) <= 64 or 91 <= ord(char) <= 96 or 123 <= ord(char) <= 126:
                symbols += 1
            else:
                return render_template("register.html", savedUsername=username, message="Invalid character in password!")

            # Break out of loop if at least 1 of each are found
            if upper > 0 and lower > 0 and numbers > 0 and symbols > 0:
                break

        # If any one of these are not found in password, password beomes invalid
        if upper == 0 or lower == 0 or numbers == 0 or symbols == 0:
            return render_template("register.html", savedUsername=username, message="Password must contain at least 1 upper case letter, lower case letter, number and symbol")

        # Password must contain 8 characters
        if len(password) < 8:
            return render_template("register.html", savedUsername=username, message="Password must be at least 8 characters long")

        # Password not the same as confirmation password
        if password != confirmation:
            return render_template("register.html", savedUsername=username, message="Password and Confirm Password do not match")

        # Convert password to hash
        Hash = generate_password_hash(password)

        # Register the user
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?);", username, Hash)

        # Initialise user specific data for user
        userID = db.execute("SELECT id FROM users WHERE username = ?;", username)[0]["id"]
        newAccountHandler(userID)

        return redirect("/login")

    return render_template("register.html")

@app.route("/logout")
def logout():

    # Clear history of user
    session.clear()

    return redirect('/')

@app.route("/run", methods=["GET", "POST"])
@login_required
def run():

    # Request sent via post
    if request.method == "POST":

        # Get updated timestamp, distance and time data when the run is reset
        userData = request.get_json()

        timestamp = userData['timestamp']
        distance = userData['distance']
        time = userData['time']
        rewards = userData['rewards']

        if len(db.execute('SELECT * FROM users WHERE id = ?;', session['user_id'])):

            # Insert data into database when account exists
            db.execute('INSERT INTO run_log (user_id, timestamp, distance, time) VALUES(?, ?, ?, ?);', session['user_id'], timestamp, distance, time)
            for i in rewards:
                db.execute('UPDATE user_collectables SET amount = amount + ? WHERE user_id = ? AND collectable_id = ?;', i['earned'], session['user_id'], int(i['id']))

        else:
            # Entering data into session for guests
            for i in rewards:
                session['user_collectables'][int(i['id'])] += i['earned']

        return jsonify({'success':True}), 200, {'ContentType':'application/json'}

    collectableTypes = db.execute("SELECT * FROM collectable_types;")
    return render_template("run.html", collectables = collectableTypes)

@app.route("/game")
@login_required
def game():

    # Get a list of all the users upgrdes bought from the shop
    userItems = db.execute('SELECT level FROM user_items WHERE user_id = ?', session['user_id'])

    # For those logged in as guest
    if not userItems:
        userItems = []
        for i in session['user_items']:
            userItems.append({'id': i, 'level': session['user_items'][i]})

    return render_template("game.html", userItems=userItems)


@app.route("/shop", methods=["GET", "POST"])
@login_required
def shop():

    # Request sent via post
    if request.method == "POST":

        # Storing the data from post request
        levels = request.get_json()['levels']
        userCollectables = request.get_json()['userCollectables']

        if len(db.execute('SELECT * FROM users WHERE id = ?', session['user_id'])):

            # For existing accounts
            for i in levels:
                db.execute('UPDATE user_items level = ? WHERE item_id = ?', levels[i], i)
            for i in userCollectables:
                db.execute('UPDATE user_collectables amount = ? WHERE collectable_id = ?', i['amount'], int(i['collectable_id']))

        else:

            # For guests
            for i in levels:
                session['user_items'][int(i)] = levels[i]
            for i in userCollectables:
                session['user_collectables'][int(i['collectable_id'])] = i['amount']


        return jsonify({'success':True}), 200, {'ContentType':'application/json'}

    # Getting a list of shop items and collectables the userr has
    shopItems = db.execute('SELECT shop_items.id AS id, name, item_types.type AS item_type, description, collectable_id, costs, user_items.level AS level FROM shop_items JOIN item_types ON shop_items.type_id = item_types.id JOIN user_items ON shop_items.id = user_items.item_id WHERE user_items.user_id = ?;', session['user_id'])
    userCollectables = db.execute('SELECT collectable_id, amount FROM user_collectables WHERE user_id = ?;', session['user_id'])

    # For guests
    if not (len(shopItems) or len(userCollectables)):
        shopItems = db.execute('SELECT shop_items.id AS id, name, item_types.type AS item_type, description, collectable_id, costs FROM shop_items JOIN item_types ON shop_items.type_id = item_types.id')
        for i in shopItems:
            i['level'] = session['user_items'][i['id']]
        for i in db.execute('SELECT id FROM collectable_types'):
            userCollectables.append({'collectable_id': i['id'], 'amount': session['user_collectables'][i['id']]})

    return render_template("shop.html", shopItems=shopItems, userCollectables=userCollectables)

@app.route("/history")
@login_required
def history():

    # Get a list of all of the user's runs
    run_log = db.execute("SELECT timestamp, distance, time FROM run_log WHERE user_id = ?;", session["user_id"])

    return render_template("history.html", run_log=run_log)