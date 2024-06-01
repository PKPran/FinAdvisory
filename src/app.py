from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required
from models import User, Transaction, Request, RequestLine
import os
from database import db
from sqlalchemy import inspect, or_
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///finadv.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()
login_manager = LoginManager(app)
login_manager.login_view = "login"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/list_database")
@login_required
def list_database():
    # Get a list of all table names
    inspector = inspect(db.engine)
    table_names = inspector.get_table_names()

    # Fetch all data from each table
    table_data = {}
    for table_name in table_names:
        table = db.metadata.tables[table_name]
        table_data[table_name] = db.session.query(table).all()
    return render_template("list_database.html", table_data=table_data)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user_name = request.form["user_name"]
        password = request.form["password"]
        first_name = request.form["first_name"]
        middle_name = request.form["middle_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        phone_number = request.form["phone_number"]
        existing_user = User.query.filter_by(user_name=user_name).first()
        existing_email = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Username already exists. Please choose a different one.", "error")
            return redirect(url_for("register"))
        elif existing_email:
            flash("Email already exists. Please use a different one.", "error")
            return redirect(url_for("register"))
        password_hash = generate_password_hash(password)

        # Create a new user object
        new_user = User(
            user_name=user_name,
            password_hash=password_hash,
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/register_ca", methods=["GET", "POST"])
def register_ca():
    if request.method == "POST":
        user_name = request.form["user_name"]
        password = request.form["password"]
        first_name = request.form["first_name"]
        middle_name = request.form["middle_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        phone_number = request.form["phone_number"]
        certificate = request.form["certificate"]
        base_fee = request.form["base_fee"]
        bank_account = request.form["bank_account"]
        ifsc = request.form["ifsc"]
        existing_user = User.query.filter_by(user_name=user_name).first()
        existing_email = User.query.filter_by(email=email).first()
        existing_phone_number = User.query.filter_by(phone_number=phone_number).first()
        existing_certificate = User.query.filter_by(certificate=certificate).first()
        if existing_user:
            flash("Username already exists. Please choose a different one.", "error")
            return redirect(url_for("register_ca"))
        elif existing_email:
            flash("Email already exists. Please use a different one.", "error")
            return redirect(url_for("register_ca"))
        elif existing_phone_number:
            flash("Phone number already exists. Please use a different one.", "error")
            return redirect(url_for("register_ca"))
        elif existing_certificate:
            flash("Certificate already exists. Please use a different one.", "error")
            return redirect(url_for("register_ca"))
        password_hash = generate_password_hash(password)
        new_ca = User(
            user_name=user_name,
            password_hash=password_hash,
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            is_ca=True,
            email=email,
            phone_number=phone_number,
            certificate=certificate,
            base_fee=base_fee,
            bank_account=bank_account,
            ifsc=ifsc,
        )
        db.session.add(new_ca)
        db.session.commit()
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("register_ca.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_name = request.form["user_name"]
        password = request.form["password"]
        user = User.query.filter_by(user_name=user_name).first()
        print("User:", user)
        if user:
            if user.check_password(password):
                login_user(user)
                flash("Login successful!", "success")
                return redirect(url_for("index"))
            else:
                flash("Incorrect password.", "danger")
        else:
            flash("Username not found.", "danger")
    return render_template("login.html")


@app.route("/find_ca", methods=["GET", "POST"])
@login_required
def find_ca():
    if request.method == "POST":
        name = request.form["name"]
        print("Name:", name)
        ca_list = User.query.filter(
            or_(User.first_name.ilike(f"%{name}%"), User.last_name.ilike(f"%{name}%")),
            User.is_ca == True,
        ).all()
        print("CA List:", ca_list)
        flash(f"Found {len(ca_list)} CAs.", "info")
        return render_template("find_ca.html", ca_list=ca_list)
    ca_list = User.query.filter(User.is_ca == True).all()
    return render_template("find_ca.html", ca_list=ca_list)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, port=5001)
