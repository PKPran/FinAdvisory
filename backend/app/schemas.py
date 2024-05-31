from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    Type: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    UID: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class CharteredAccountantBase(BaseModel):
    UID: int
    certificate_number: str
    fee: int
    bank_account: str
    specialization: str


class CharteredAccountantCreate(CharteredAccountantBase):
    pass


class CharteredAccountant(CharteredAccountantBase):
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class TransactionBase(BaseModel):
    customer_id: int
    chartered_accountant_id: int
    date: datetime
    amount: int
    status: str


class TransactionCreate(TransactionBase):
    pass


class Transaction(TransactionBase):
    UID: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class RequestBase(BaseModel):
    customer_id: int
    chartered_accountant_id: int
    date: datetime
    status: str


class RequestCreate(RequestBase):
    pass


class Request(RequestBase):
    UID: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class RequestLineBase(BaseModel):
    request_id: int
    customer_id: int
    chartered_accountant_id: int
    date: datetime
    party: str
    status: str


class RequestLineCreate(RequestLineBase):
    pass


class RequestLine(RequestLineBase):
    UID: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
