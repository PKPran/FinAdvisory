import pytz
from datetime import datetime
from uuid import uuid4
from werkzeug.security import generate_password_hash
import platform
import math
import re


def generate_uuid():
    return str(uuid4())


def get_ist_time():
    ist = pytz.timezone("Asia/Kolkata")
    return datetime.now(ist)


def finadv_gen_hash(password):
    current_os = platform.system()
    if current_os == "Darwin" or current_os == "Linux":
        return generate_password_hash(password, method="pbkdf2")
    return generate_password_hash(password)
