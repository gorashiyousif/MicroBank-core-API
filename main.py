import os
import psycopg2
import bcrypt
import jwt
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="MicroBank Core Live Infrastructure", version="2026.1.0")

# Unified Explicit Cloud Connection String
CLOUD_DB_URL = "postgresql://gorashi_user:m4pLF12pqPIUE4WAISrezAnicTKMxaK6@://render.com"

class TransferPayload(BaseModel):
    sender_id: int
    receiver_id: int
    amount: float

@app.get("/")
def read_root():
    return {"status": "Active", "system": "MicroBank Core Web API", "engineer": "Gorashi Yousif"}

@app.get("/balance/{account_id}")
def get_balance(account_id: int):
    connection = None
    try:
        # [FORCE BOUND]: Direct injection to break any server socket routing cache
        connection = psycopg2.connect(CLOUD_DB_URL)
        cursor = connection.cursor()
        cursor.execute("SELECT account_id, name, balance FROM Accounts WHERE account_id = %s;", (account_id,))
        account = cursor.fetchone()
        cursor.close()
        
        if not account:
            raise HTTPException(status_code=404, detail="Financial routing node not found")
            
        return {
            "account_id": int(account[0]), 
            "name": str(account[1]), 
            "balance": float(account[2])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Framework Failure: {str(e)}")
    finally:
        if connection:
            connection.close()
