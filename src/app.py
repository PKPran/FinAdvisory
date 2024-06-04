from flask import Flask, render_template, request, redirect, url_for, flash
from flask_socketio import SocketIO, emit
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from models import User, Request, RequestLine, Message, Transaction
import os
from database import db
from sqlalchemy import inspect, or_
from utils import finadv_gen_hash
from utils import get_ist_time, generate_uuid, get_request_data
import razorpay

razorpay_client = razorpay.Client(
    auth=("rzp_test_Q7dYN8I5O4YPOu", "Jmfll5EsRzxHuIQd7W6T2ltC")
)

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
    ca_list = User.query.filter(User.is_ca == True).all()
    request_data = (
        get_request_data(current_user) if current_user.is_authenticated else []
    )
    return render_template("index.html", ca_list=ca_list, requests=request_data)


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


@socketio.on("connect")
@login_required
def handle_connect():
    emit("connected", {"msg": "Connected"})


@socketio.on("disconnect")
@login_required
def handle_disconnect():
    logout_user()
    emit("disconnected", {"msg": "Disconnected"})


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
        password_hash = finadv_gen_hash(password)
        new_user = User(
            uuid=generate_uuid(),
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
        password_hash = finadv_gen_hash(password)
        new_ca = User(
            uuid=generate_uuid(),
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
        remember = True if request.form.get("remember") else False
        user = User.query.filter_by(user_name=user_name).first()
        if user:
            if user.check_password(password):
                login_user(user, remember=remember)
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
            uuid=generate_uuid(),
            customer_uuid=current_user.uuid,
            ca_uuid=str(ca_uuid),
            date=get_ist_time(),
            party_name=current_user.full_name(),
            status="Submitted",
            description=description,
        )
        db.session.add(new_request_line)
        new_request = Request(
            uuid=generate_uuid(),
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


@app.route("/view_requests", methods=["GET", "POST"])
@login_required
def view_requests():
    request_data = get_request_data(current_user)
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
        uuid=generate_uuid(),
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


@app.route("/chat")
@login_required
def chat():
    if current_user.is_ca:
        request_approved = Request.query.filter_by(
            ca_uuid=current_user.uuid, status="Accepted"
        ).all()
    else:
        request_approved = Request.query.filter_by(
            customer_uuid=current_user.uuid, status="Accepted"
        ).all()
    chat_users = []
    for request in request_approved:
        if current_user.is_ca:
            user = User.query.filter_by(uuid=request.customer_uuid).first()
        else:
            user = User.query.filter_by(uuid=request.ca_uuid).first()
        chat_users.append(user)
    for chat_user in chat_users:
        chat_user.messages = Message.query.filter(
            or_(
                Message.sender_id == current_user.uuid,
                Message.recipient_id == current_user.uuid,
            ),
            or_(
                Message.sender_id == chat_user.uuid,
                Message.recipient_id == chat_user.uuid,
            ),
        ).all()
    if chat_users[0].messages:
        chat_users = sorted(
            chat_users, key=lambda x: x.messages[-1].timestamp, reverse=True
        )
    return render_template("chat.html", chat_users=chat_users)


@socketio.on("private_message")
@login_required
def handle_private_message(data):
    sender = current_user.uuid
    recipient = data["recipient"].replace("message-form-", "")
    message = data["message"]
    print("sender", sender)
    print("recipient", recipient)
    print("message", message)
    new_message = Message(sender_id=sender, recipient_id=recipient, body=message)
    print("new_message", new_message)
    db.session.add(new_message)
    db.session.commit()
    emit("private_message", {"sender": sender, "message": message}, room=recipient)


@socketio.on("message")
def handle_message(data):
    print("data", data)
    sender = data["sender"]
    recipient = data["recipient"]
    body = data["body"]
    message = Message(sender=sender, recipient=recipient, body=body)
    db.session.add(message)
    db.session.commit()
    emit("message", data, broadcast=True)


@app.route("/contact_us", methods=["GET", "POST"])
def contact_us():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        message = request.form["message"]
        new_message = Message(
            sender_id="Contact Us",
            recipient_id="Admin",
            body=f"Name: {name}\nEmail: {email}\nMessage: {message}",
        )
        db.session.add(new_message)
        db.session.commit()
        flash("Message sent successfully.", "success")
        return redirect(url_for("index"))
    return render_template("contact_us.html")


@app.route("/update_profile/<uuid:uuid>", methods=["GET", "POST"])
@login_required
def update_profile(uuid):
    user = User.query.filter_by(uuid=str(uuid)).first()
    if request.method == "POST":
        user.first_name = request.form["first_name"]
        user.middle_name = request.form["middle_name"]
        user.last_name = request.form["last_name"]
        user.email = request.form["email"]
        user.phone_number = request.form["phone_number"]
        if user.is_ca:
            user.certificate = request.form["certificate"]
            user.base_fee = request.form["base_fee"]
            user.bank_account = request.form["bank_account"]
            user.ifsc = request.form["ifsc"]
        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("view_profile", uuid=user.uuid))
    return render_template("update_profile.html", user=user)


@app.route("/settings", methods=["GET"])
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


@app.route("/make_payment/<float:amount>", methods=["GET", "POST"])
@login_required
def make_payment(amount):
    if request.method == "POST":
        flash("Payment successful.", "success")
        return redirect(url_for("view_requests"))
    return render_template("make_payment.html", amount=amount)


@app.route("/charge", methods=["POST"])
def charge():
    payment_data = request.get_json()
    payment_id = payment_data.get("payment_id", None)
    amount = payment_data.get("amount", None)
    ca_name = payment_data.get("ca_name", None)
    request_uuid = payment_data.get("request_uuid", None)
    razorpay_client.payment.capture(payment_id, int(round(float(amount) * 100)))
    new_transaction = Transaction(
        uuid=generate_uuid(),
        amount=amount,
        bank_account=current_user.bank_account,
        customer_uuid=current_user.uuid,
        ca_uuid=ca_name,
        request_id=request_uuid,
        date=get_ist_time(),
        payment_id=payment_id,
    )
    db.session.add(new_transaction)
    db.session.commit()
    flash("Payment successful.", "success")
    return redirect(url_for("view_requests"))


if __name__ == "__main__":
    socketio.run(app, port=5001, debug=True)
