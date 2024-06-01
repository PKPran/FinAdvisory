from flask import Flask, render_template, request, redirect, url_for, flash
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from models import User, Transaction, Request, RequestLine
import os
from database import db
from sqlalchemy import inspect, or_
from werkzeug.security import generate_password_hash
import datetime
from utils import get_ist_time

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///finadv.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
socketio = SocketIO(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
db.init_app(app)

with app.app_context():
    db.create_all()



@app.route("/")
def index():
    return render_template("index.html")


@app.route("/list_database")
def list_database():
    inspector = inspect(db.engine)
    table_names = inspector.get_table_names()
    table_data = {}
    for table_name in table_names:
        table = db.metadata.tables[table_name]
        table_data[table_name] = db.session.query(table).all()
    return render_template("list_database.html", table_data=table_data)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@socketio.on('connect')
@login_required
def handle_connect():
    emit('connected', {'msg': 'Connected'})

@socketio.on('disconnect')
@login_required
def handle_disconnect():
    logout_user()
    emit('disconnected', {'msg': 'Disconnected'})

@socketio.on('private_message')
@login_required
def handle_private_message(data):
    sender = current_user.username
    recipient = data['recipient']
    message = data['message']
    # Save message to database
    new_message = Message(sender=sender, recipient=recipient, message=message)
    db.session.add(new_message)
    db.session.commit()
    # Emit the message to the recipient
    emit('private_message', {'sender': sender, 'message': message}, room=recipient)

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


@app.route("/book_ca/<uuid:ca_uuid>", methods=["GET", "POST"])
@login_required
def book_ca(ca_uuid):
    print("CA UUID:", ca_uuid)
    ca = User.query.filter_by(uuid=str(ca_uuid)).first()
    print("CA:", ca)
    if request.method == "POST":
        description = request.form["description"]
        new_request_line = RequestLine(
            customer_uuid=current_user.uuid,
            ca_uuid=str(ca_uuid),
            date=get_ist_time(),
            party_name=current_user.full_name(),
            status="Submitted",
            description=description,
        )
        db.session.add(new_request_line)
        new_request = Request(
            customer_uuid=current_user.uuid,
            ca_uuid=str(ca_uuid),
            date=get_ist_time(),
            party_name=current_user.full_name(),
            status="Submitted",
            description=description,
        )
        db.session.add(new_request)
        db.session.commit()
        flash("Request sent successfully.", "success")
        return redirect(url_for("index"))
    return render_template("book_ca.html", ca=ca)


@app.route("/view_profile/<uuid:uuid>", methods=["GET", "POST"])
@login_required
def view_profile(uuid):
    user = User.query.filter_by(uuid=str(uuid)).first()
    return render_template("view_profile.html", user=user)


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        user = User.query.filter_by(uuid=current_user.uuid).first()
        user.first_name = request.form["first_name"]
        user.middle_name = request.form["middle_name"]
        user.last_name = request.form["last_name"]
        user.email = request.form["email"]
        user.phone_number = request.form["phone_number"]
        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("index"))
    return render_template("settings.html")


@app.route("/view_requests", methods=["GET", "POST"])
@login_required
def view_requests():
    request_data = []
    if current_user.is_ca:
        requests = Request.query.filter_by(ca_uuid=current_user.uuid).all()
        for request in requests:
            customer = User.query.filter_by(uuid=request.customer_uuid).first()
            request_data.append(
                {
                    "request": request,
                    "customer_name": customer.full_name(),
                    "amount": current_user.base_fee,
                    "status": request.status,
                    "email": customer.email,
                }
            )
    else:
        requests = Request.query.filter_by(customer_uuid=current_user.uuid).all()
        for request in requests:
            ca = User.query.filter_by(uuid=request.ca_uuid).first()
            request_data.append(
                {
                    "request": request,
                    "ca_name": ca.full_name(),
                    "amount": ca.base_fee,
                    "status": request.status,
                    "email": ca.email,
                }
            )
    return render_template("view_requests.html", requests=request_data)


@app.route("/cancel_request/<uuid:uuid>", methods=["GET", "POST"])
@login_required
def cancel_request(uuid):
    request = Request.query.filter_by(uuid=str(uuid)).first()
    request.status = "Cancelled by User"
    db.session.commit()
    flash("Request cancelled successfully.", "success")
    return redirect(url_for("view_requests"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


@app.route("/update_request/<string:uuid>/<string:status>", methods=["GET", "POST"])
@login_required
def update_request(uuid, status):
    request = Request.query.filter_by(uuid=str(uuid)).first()
    request.status = status
    new_request_line = RequestLine(
        customer_uuid=request.customer_uuid,
        ca_uuid=request.ca_uuid,
        date=get_ist_time(),
        party_name=current_user.full_name(),
        status=status,
        description=request.description,
    )
    db.session.add(new_request_line)
    db.session.commit()
    flash("Request updated successfully.", "success")
    return redirect(url_for("view_requests"))


if __name__ == '__main__':
    socketio.run(app, port=5001, debug=True)
