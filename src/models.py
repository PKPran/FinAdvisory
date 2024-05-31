# models.py

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin):
    def __init__(self, username, password, first_name, middle_name, last_name, is_ca):
        self.username = username
        self.password_hash = generate_password_hash(password = password, method = 'pbkdf2:sha256')
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.is_ca = is_ca

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
