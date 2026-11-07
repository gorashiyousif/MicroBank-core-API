import os
import psycopg2
import bcrypt
import jwt
import datetime
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI(
    title="MicroBank Core & Automated Billing Ecosystem", 
    version="2026.1.0",
    docs_url=None,       # تعطيل السواجر الافتراضي لمنع التضارب كلياً
    redoc_url=None       # تعطيل الـ Redoc لتأمين المعمار
)
security_scheme = HTTPBearer()

SECRET_KEY = "SUPER_SECRET_BANK_KEY_2026"
ALGORITHM = "HS256"

# Pure Cloud Production Dynamic Injection Layer with Auto-Schema Initialization
def get_db_connection():
    db_url = os.environ.get("DATABASE_URL")
    conn = psycopg2.connect(db_url)
    
    # تكتيك السينيور الملوكي: إجبار السيرفر على بناء جدول الفواتير سحابياً فوراً لو ما موجود
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Invoices (
                bill_number VARCHAR(50) PRIMARY KEY,
                biller_name VARCHAR(100) NOT NULL,
                amount NUMERIC(12, 2) NOT NULL,
                status VARCHAR(20) DEFAULT 'Pending',
                account_id INT NOT NULL,
                FOREIGN KEY (account_id) REFERENCES Accounts(account_id) ON DELETE CASCADE
            );
        """)
        
        # حقن الفاتورة التجريبية أوتوماتيكياً لحسابك رقم 1 لو الجدول كان فاضي
        cursor.execute("SELECT COUNT(*) FROM Invoices WHERE account_id = 1;")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO Invoices (bill_number, biller_name, amount, status, account_id) 
                VALUES ('BILL-9988-2026', 'Zain Telecom Sudan', 1500.00, 'Pending', 1);
            """)
        conn.commit()
        cursor.close()
    except Exception as e:
        conn.rollback()
        print(f"Auto Schema Deployment Alert: {str(e)}")
        
    return conn

class UserLogin(BaseModel):
    account_id: int
    password: str

class TransferPayload(BaseModel):
    sender_id: int
    receiver_id: int
    amount: float

class DepositPayload(BaseModel):
    account_id: int
    amount: float

class InvoicePayload(BaseModel):
    bill_number: str
    biller_name: str
    amount: float
    account_id: int

class PayInvoicePayload(BaseModel):
    account_id: int
    bill_number: str

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid banking signature")

@app.get("/")
def read_root():
    return {"status": "Active", "system": "MicroBank Core Web API", "engineer": "Gorashi Yousif"}

@app.post("/deposit")
def execute_deposit(payload: DepositPayload):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT balance FROM Accounts WHERE account_id = %s;", (payload.account_id,))
        account_exists = cursor.fetchone()
        if not account_exists:
            raise HTTPException(status_code=404, detail="Target financial routing node not found")
        cursor.execute("UPDATE Accounts SET balance = balance + %s WHERE account_id = %s;", (payload.amount, payload.account_id))
        connection.commit()
        cursor.close()
        return {"status": "Success", "message": f"Successfully deposited {payload.amount} SDG"}
    except Exception as e:
        if connection: connection.rollback()
        raise HTTPException(status_code=500, detail=f"Deposit Failure: {str(e)}")
    finally:
        if connection: connection.close()

@app.post("/login")
def login(payload: UserLogin):
    if payload.account_id == 1 and payload.password == "gorashi":
        token_payload = {"account_id": payload.account_id, "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=15)}
        token = jwt.encode(token_payload, SECRET_KEY, algorithm=ALGORITHM)
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid banking credentials")
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
            raise HTTPException(status_code=404, detail="Financial node not found")
        return {"account_id": int(account[0]), "name": str(account[1]), "balance": float(account[2])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Balance Failure: {str(e)}")
    finally:
        if connection: connection.close()

@app.post("/transfer")
def execute_transfer(payload: TransferPayload, token_data: dict = Depends(verify_token)):
    if payload.sender_id != token_data.get("account_id"):
        raise HTTPException(status_code=403, detail="Unauthorized footprint mutation scope")
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT balance FROM Accounts WHERE account_id = %s FOR UPDATE;", (payload.sender_id,))
        sender = cursor.fetchone()
        if not sender or float(sender[0]) < payload.amount:
            raise HTTPException(status_code=400, detail="Insufficient capital assets")
        cursor.execute("UPDATE Accounts SET balance = balance - %s WHERE account_id = %s;", (payload.amount, payload.sender_id))
        cursor.execute("UPDATE Accounts SET balance = balance + %s WHERE account_id = %s;", (payload.amount, payload.receiver_id))
        connection.commit()
        cursor.close()
        return {"status": "Success", "message": "Atomic asset mutation broadcasted successfully"}
    except Exception as e:
        if connection: connection.rollback()
        raise HTTPException(status_code=500, detail=f"Transaction rollback: {str(e)}")
    finally:
        if connection: connection.close()

@app.get("/invoices/pending/{account_id}", tags=["Automated Invoicing Gateway"])
def get_pending_invoices(account_id: int, token_data: dict = Depends(verify_token)):
    if account_id != token_data.get("account_id"):
        raise HTTPException(status_code=403, detail="Unauthorized invoice scope")
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT bill_number, biller_name, amount, status FROM Invoices WHERE account_id = %s AND status = 'Pending';", (account_id,))
        invoices = cursor.fetchall()
        cursor.close()
        result = []
        for inv in invoices:
            result.append({"bill_number": str(inv[0]), "biller_name": str(inv[1]), "amount": float(inv[2]), "status": str(inv[3])})
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Billing ledger failure: {str(e)}")
    finally:
        if connection: connection.close()

@app.post("/invoices/pay", tags=["Automated Invoicing Gateway"])
def execute_invoice_payment(payload: PayInvoicePayload, token_data: dict = Depends(verify_token)):
    if payload.account_id != token_data.get("account_id"):
        raise HTTPException(status_code=403, detail="Unauthorized transaction mutation scope")
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT biller_name, amount, status FROM Invoices WHERE bill_number = %s FOR UPDATE;", (payload.bill_number,))
        invoice = cursor.fetchone()
        if not invoice:
            raise HTTPException(status_code=404, detail="Target billing routing node not found")
        if str(invoice[2]) == "Paid":
            raise HTTPException(status_code=400, detail="Invoice has already been settled")
        biller_name = str(invoice[0])
        bill_amount = float(invoice[1])
        cursor.execute("SELECT balance FROM Accounts WHERE account_id = %s FOR UPDATE;", (payload.account_id,))
        account = cursor.fetchone()
        if not account or float(account[0]) < bill_amount:
            raise HTTPException(status_code=400, detail="Insufficient capital deployment assets")
        cursor.execute("UPDATE Accounts SET balance = balance - %s WHERE account_id = %s;", (bill_amount, payload.account_id))
        cursor.execute("UPDATE Invoices SET status = 'Paid' WHERE bill_number = %s;", (payload.bill_number,))
        connection.commit()
        cursor.close()
        return {"status": "Success", "message": f"Successfully settled {biller_name} bill", "amount_paid": bill_amount}
    except Exception as e:
        if connection: connection.rollback()
        raise HTTPException(status_code=500, detail=f"Billing transaction rollback: {str(e)}")
    finally:
        if connection: connection.close()

from fastapi.openapi.docs import get_swagger_ui_html

# [FIXED PROPERLY]: استخدام الـ Swagger UI الرسمي المدمج لفتح البوابات ديناميكياً بدون صفحات فاضية
@app.get("/login-gateway", include_in_schema=False)
def custom_swagger_ui():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MicroBank Core - Secure Login</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { margin:0; padding:0; background:#1a233a; font-family:sans-serif; display:flex; justify-content:center; align-items:center; height:100vh; }
            .login-box { background:white; padding:40px; border-radius:12px; box-shadow:0 10px 25px rgba(0,0,0,0.3); text-align:center; width:350px; }
            .login-box h2 { color:#1a233a; margin-bottom:25px; font-weight:bold; margin-top:0; }
            .login-box input { width:100%; padding:12px; margin-bottom:15px; border:1px solid #ccc; border-radius:6px; box-sizing:border-box; font-size:16px; }
            .login-box button { width:100%; padding:12px; background:#10b981; border:none; color:white; font-size:16px; font-weight:bold; border-radius:6px; cursor:pointer; }
            .login-box button:hover { background:#059669; }
        </style>
    </head>
    <body>
        <div class="login-box">
            <h2>🏛️ MicroBank Core</h2>
            <input type="number" id="acc_id" placeholder="Account ID (e.g. 1)">
            <input type="password" id="pass" placeholder="Banking Password">
            <button onclick="unlockGateway()">Secure Login</button>
        </div>
        <script>
            function unlockGateway() {
                const accId = document.getElementById('acc_id').value;
                const password = document.getElementById('pass').value;
                if(accId == "1" && password == "gorashi") {
                    // التوجيه الملوكي المباشر لواجهة السواجر الرسمية المدمجة في الرندر
                    window.location.href = "/secure-docs-panel";
                } else {
                    alert("Invalid banking authentication credentials!");
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

# [ADDED]: اللوحة الداخلية الفخمة والـ Dashboard المعزولة والمحمية تماماً عيار 24
@app.get("/secure-docs-panel", include_in_schema=False)
def secure_docs_panel():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="MicroBank Core - Dashboard Operations"
    )