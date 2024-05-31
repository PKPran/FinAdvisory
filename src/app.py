from bson import ObjectId
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_pymongo import PyMongo
from flask_login import LoginManager, login_user, logout_user, login_required
from models import User

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/"
mongo = PyMongo(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"


@app.route("/")
def index():
    return render_template("index.html")


@login_manager.user_loader
def load_user(user_id):
    user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if user_data:
        return User(user_data["username"], user_data["password_hash"])
    return None


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        first_name = request.form["first_name"]
        middle_name = request.form["middle_name"]
        last_name = request.form["last_name"]
        is_ca = False
        new_user = User(
            username=username,
            password=password,
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            is_ca=is_ca,
        )
        mongo.db.users.insert_one(new_user.__dict__)
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user_data = mongo.db.users.find_one({"username": username})
        if user_data:
            user = User(user_data["username"], user_data["password_hash"])
            if user.check_password(password):
                login_user(user)
                flash("Login successful!", "success")
                return redirect(url_for("index"))
            else:
                flash("Incorrect password.", "danger")
        else:
            flash("Username not found.", "danger")

    return render_template("login.html")



if __name__ == "__main__":
    app.run(debug=True, port=5001)
