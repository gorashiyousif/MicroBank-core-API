import os
import psycopg2
import bcrypt
import jwt
import datetime
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional
from apscheduler.schedulers.background import BackgroundScheduler

app = FastAPI(title="MicroBank Core & Automated Billing Ecosystem", version="2026.1.0")

SECRET_KEY = "SUPER_SECRET_BANK_KEY_2026"
ALGORITHM = "HS256"

# Cloud PostgreSQL Connection Layer
def get_db_connection():
    import os
    # بتقرأ الرابط السحابي تلقائياً من متغيرات البيئة المؤمنة في السيرفر
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        db_url = "postgresql://gorashi_user:m4pLF12pqPIUE4WAISrezAnicTKMxaK6@://render.com"
    return psycopg2.connect(db_url)
# Pydantic Schemas
class UserLogin(BaseModel):
    account_id: int
    password: str

class TransferPayload(BaseModel):
    sender_id: int
    receiver_id: int
    amount: float

# Token Verification Dependency
def verify_token(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed authorization header")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Security token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid security signature")

# Automated Billing Cron-Job Function
def auto_billing_job():
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Scan for Unpaid invoices triggered by scheduling intervals
        cursor.execute("SELECT invoice_id, account_id, billing_amount FROM Invoices WHERE status = 'Unpaid';")
        pending_invoices = cursor.fetchall()
        
        for invoice in pending_invoices:
            inv_id, acc_id, amount = invoice
            
            # Atomic transactional isolation check per ledger record
            cursor.execute("SELECT balance FROM Accounts WHERE account_id = %s FOR UPDATE;", (acc_id,))
            account_data = cursor.fetchone()
            
            if account_data and float(account_data[0]) >= float(amount):
                # Debit customer wallet safely inside database constraint limits
                cursor.execute("UPDATE Accounts SET balance = balance - %s WHERE account_id = %s;", (amount, acc_id))
                # Credit enterprise settlement ledger account
                cursor.execute("UPDATE Accounts SET balance = balance + %s WHERE account_id = 999;", (amount,))
                # Mutate invoice operational state matrix
                cursor.execute("UPDATE Invoices SET status = 'Paid' WHERE invoice_id = %s;", (inv_id,))
            else:
                # Flag insufficient funding overflows dynamically to Overdue status
                cursor.execute("UPDATE Invoices SET status = 'Overdue' WHERE invoice_id = %s;", (inv_id,))
                
        connection.commit()
        cursor.close()
    except Exception as e:
        if connection:
            connection.rollback()
    finally:
        if connection:
            connection.close()

# Background Scheduler Task Runner Infrastructure
scheduler = BackgroundScheduler()
scheduler.add_job(auto_billing_job, 'interval', minutes=1)
scheduler.start()

# API Endpoints
@app.get("/")
def read_root():
    return {
        "status": "Active",
        "system": "MicroBank Core Web API",
        "engineer": "Gorashi Yousif"
    }

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
            
        return {"account_id": account[0], "name": account[1], "balance": float(account[2])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")
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
