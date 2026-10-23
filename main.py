import os
import psycopg2
import bcrypt
import jwt
import datetime
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="MicroBank Core & Automated Billing Ecosystem", version="2026.1.0")

SECRET_KEY = "SUPER_SECRET_BANK_KEY_2026"
ALGORITHM = "HS256"

# Dynamic Environment Injection Layer for Cloud Production
def get_db_connection():
    # بتقرأ الـ Value الجاهز والمصلح الـ في الـ Render أوتوماتيكياً بدون لخبطة
    db_url = os.environ.get("DATABASE_URL")
    return psycopg2.connect(db_url)

class UserLogin(BaseModel):
    account_id: int
    password: str

class TransferPayload(BaseModel):
    sender_id: int
    receiver_id: int
    amount: float

def verify_token(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed authorization header")
    token = authorization.split(" ") if " " in authorization else authorization
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Security token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid security signature")

@app.get("/")
def read_root():
    return {"status": "Active", "system": "MicroBank Core Web API", "engineer": "Gorashi Yousif"}

@app.post("/login")
def login(payload: UserLogin):
    if payload.account_id == 1 and payload.password == "gorashi":
        token_payload = {
            "account_id": payload.account_id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
        }
        token = jwt.encode(token_payload, SECRET_KEY, algorithm=ALGORITHM)
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid banking authentication credentials")

# [FIXED PROPERLY]: Explicit indexing mapping from PostgreSQL database tuple results
@app.get("/balance/{account_id}")
def get_balance(account_id: int):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT account_id, name, balance FROM Accounts WHERE account_id = %s;", (account_id,))
        account = cursor.fetchone()
        cursor.close()
        
        if not account:
            raise HTTPException(status_code=404, detail="Financial routing node not found")
            
        # Mapping clean explicit primitive data components securely
        return {
            "account_id": int(account[0]), 
            "name": str(account[1]), 
            "balance": float(account[2])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ledger Processing Matrix Failure: {str(e)}")
    finally:
        if connection:
            connection.close()

@app.post("/transfer")
def execute_transfer(payload: TransferPayload, token_data: dict = Depends(verify_token)):
    if payload.sender_id != token_data.get("account_id"):
        raise HTTPException(status_code=403, detail="Unauthorized transaction footprint mutation scope")
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT balance FROM Accounts WHERE account_id = %s FOR UPDATE;", (payload.sender_id,))
        sender = cursor.fetchone()
        if not sender or float(sender[0]) < payload.amount:
            raise HTTPException(status_code=400, detail="Insufficient capital deployment assets")
        cursor.execute("UPDATE Accounts SET balance = balance - %s WHERE account_id = %s;", (payload.amount, payload.sender_id))
        cursor.execute("UPDATE Accounts SET balance = balance + %s WHERE account_id = %s;", (payload.amount, payload.receiver_id))
        connection.commit()
        cursor.close()
        return {"status": "Success", "message": "Atomic asset mutation broadcasted successfully"}
    except Exception as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Transaction voided via rollback: {str(e)}")
    finally:
        if connection:
            connection.close()
