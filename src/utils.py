import pytz
from datetime import datetime
from uuid import uuid4


def generate_uuid():
    return str(uuid4())


def get_ist_time():
    ist = pytz.timezone("Asia/Kolkata")
    return datetime.now(ist)
