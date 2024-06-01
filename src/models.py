import datetime
from sqlalchemy import (
    Column,
    Enum,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Float,
)
from sqlalchemy import event
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from uuid import uuid4
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from database import db


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(80), unique=True, nullable=False, default=str(uuid4()))
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, onupdate=datetime.datetime.utcnow, default=datetime.datetime.utcnow)
    first_name = Column(String(80), nullable=False)
    middle_name = Column(String(80))
    last_name = Column(String(80), nullable=False)
    user_name = Column(String(80), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    email = Column(String(80), unique=True, nullable=False)
    phone_number = Column(String(80), unique=True, nullable=False)
    transactions = relationship("Transaction", backref="user")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User(username='{self.user_name}')>"


class CA(db.Model):
    __tablename__ = "ca"
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(80), unique=True, nullable=False, default=str(uuid4()))
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, onupdate=datetime.datetime.utcnow)
    first_name = Column(String(80), nullable=False)
    middle_name = Column(String(80))
    last_name = Column(String(80), nullable=False)
    user_name = Column(String(80), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    email = Column(String(80), unique=True, nullable=False)
    phone_number = Column(String(80), unique=True, nullable=False)
    certificate = Column(String(255))
    base_fee = Column(Float)
    bank_account = Column(String(80))
    ifsc = Column(String(80))
    transactions = relationship("Transaction", backref="ca")
    requests = relationship("Request", backref="ca")


class Transaction(db.Model):
    __tablename__ = "transaction"
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(80), unique=True, nullable=False, default=str(uuid4()))
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, onupdate=datetime.datetime.utcnow)
    amount = Column(Float, nullable=False)
    bank_account = Column(String(80))
    user_id = Column(Integer, ForeignKey("user.uuid"))
    ca_id = Column(Integer, ForeignKey("ca.uuid"))
    request_id = Column(Integer, ForeignKey("request.uuid"))
    date = Column(DateTime, nullable=False)


class Request(db.Model):
    __tablename__ = "request"
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(80), unique=True, nullable=False, default=str(uuid4()))
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, onupdate=datetime.datetime.utcnow)
    customer_id = Column(Integer, ForeignKey("user.uuid"))
    ca_id = Column(Integer, ForeignKey("ca.uuid"))
    date = Column(DateTime, nullable=False)
    request_lines = relationship("RequestLine", backref="request")
    party_name = Column(String(80))

    @property
    def current_status(self):  # Renamed the property
        if self.request_lines:
            return max(self.request_lines, key=lambda line: line.date).status
        return None


class RequestLine(db.Model):
    __tablename__ = "request_line"
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(80), unique=True, nullable=False, default=str(uuid4()))
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, onupdate=datetime.datetime.utcnow)
    ca_id = Column(Integer, ForeignKey("ca.uuid"))
    customer_id = Column(Integer, ForeignKey("user.uuid"))
    party = Column(String(80))
    request_id = Column(Integer, ForeignKey("request.uuid"))
    date = Column(DateTime, nullable=False)
    status = Column(
        Enum("Submitted", "Accepted", "Rejected", name="status"), default="Submitted"
    )