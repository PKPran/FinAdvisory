from fastapi import FastAPI, HTTPException
from .schemas import UserCreate, CharteredAccountantCreate, TransactionCreate, RequestCreate, User, CharteredAccountant, Transaction, Request, RequestLineCreate
from .supabase_client import supabase

app = FastAPI()

@app.post("/users/")
async def create_user(user: UserCreate):
    response = supabase.table('users').insert(user.dict()).execute()
    if response.status_code != 201:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

@app.post("/chartered_accountants/")
async def create_chartered_accountant(chartered_accountant: CharteredAccountantCreate):
    response = supabase.table('chartered_accountants').insert(chartered_accountant.dict()).execute()
    if response.status_code != 201:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

@app.post("/transactions/")
async def create_transaction(transaction: TransactionCreate):
    response = supabase.table('transactions').insert(transaction.dict()).execute()
    if response.status_code != 201:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

@app.post("/requests/")
async def create_request(request: RequestCreate):
    response = supabase.table('requests').insert(request.dict()).execute()
    if response.status_code != 201:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

@app.post("/request_lines/")
async def create_request_line(request_line: RequestLineCreate):
    response = supabase.table('request_lines').insert(request_line.dict()).execute()
    if response.status_code != 201:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()
