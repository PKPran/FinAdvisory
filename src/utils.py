import pytz
from datetime import datetime
from uuid import uuid4
from werkzeug.security import generate_password_hash
import platform

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

def get_request_data(current_user):
    from models import Request, User
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
    return request_data