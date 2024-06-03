from sqlalchemy import (
    Column,
    Enum,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Float,
    Boolean,
)
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from utils import generate_uuid, get_ist_time

class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(80), unique=True, nullable=False)
    created_at = Column(DateTime, nullable=False, default=get_ist_time())
    updated_at = Column(
        DateTime, nullable=False, onupdate=get_ist_time(), default=get_ist_time()
    )
    first_name = Column(String(80), nullable=False)
    middle_name = Column(String(80))
    last_name = Column(String(80), nullable=False)
    user_name = Column(String(80), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    email = Column(String(80), unique=True, nullable=False)
    is_ca = Column(Boolean, nullable=False, default=False)
    phone_number = Column(String(80), unique=True, nullable=False)
    certificate = Column(String(255), unique=True, nullable=True)
    base_fee = Column(Float, nullable=True)
    bank_account = Column(String(80), nullable=True)
    ifsc = Column(String(80), nullable=True)
    transactions = relationship("Transaction", backref="user")
    requests = relationship("Request", backref="user")
    sent_messages = relationship('Message', backref='sender', lazy='dynamic', foreign_keys='Message.sender_id')
    received_messages = relationship('Message', backref='recipient', lazy='dynamic', foreign_keys='Message.recipient_id')

    def full_name(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method="pbkdf2")

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User(username='{self.user_name}')>"


class Transaction(db.Model):
    __tablename__ = "transaction"
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(80), unique=True, nullable=False)
    created_at = Column(DateTime, nullable=False, default=get_ist_time())
    updated_at = Column(DateTime, nullable=False, onupdate=get_ist_time(), default=get_ist_time())
    amount = Column(Float, nullable=False)
    bank_account = Column(String(80))
    customer_uuid = Column(Integer, ForeignKey("user.uuid"))
    ca_uuid = Column(String(80))
    request_id = Column(Integer, ForeignKey("request.uuid"))
    date = Column(DateTime, nullable=False)
    payment_id = Column(String(80))


class Request(db.Model):
    __tablename__ = "request"
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(80), unique=True, nullable=False)
    created_at = Column(DateTime, nullable=False, default=get_ist_time())
    updated_at = Column(DateTime, nullable=False, onupdate=get_ist_time(), default=get_ist_time())
    customer_uuid = Column(Integer, ForeignKey("user.uuid"))
    ca_uuid = Column(String(80))
    date = Column(DateTime, nullable=False)
    description = Column(String(255))
    request_lines = relationship("RequestLine", backref="request")
    party_name = Column(String(80))
    status = Column(
        Enum("Submitted", "Accepted", "Rejected", "Cancelled by User", name="status"), default="Submitted"
    )


class RequestLine(db.Model):
    __tablename__ = "request_line"
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(80), unique=True, nullable=False)
    created_at = Column(DateTime, nullable=False, default=get_ist_time())
    updated_at = Column(
        DateTime, nullable=False, onupdate=get_ist_time(), default=get_ist_time()
    )
    customer_uuid = Column(Integer, ForeignKey("user.uuid"))
    ca_uuid = Column(String(80))
    party_name = Column(String(80))
    request_id = Column(Integer, ForeignKey("request.uuid"))
    date = Column(DateTime, nullable=False)
    description = Column(String(255))
    status = Column(
        Enum("Submitted", "Accepted", "Rejected", "Cancelled by User", name="status"), default="Submitted"
    )

class Message(db.Model):
    id = Column(Integer, primary_key=True)
    sender_id = Column(String, ForeignKey('user.uuid'))
    recipient_id = Column(String, ForeignKey('user.uuid'))
    body = Column(String(500))
    timestamp = Column(DateTime, index=True, default=get_ist_time())

    def __repr__(self):
        return f'<Message {self.body}>'