import os
import psycopg2
import bcrypt
import jwt
import datetime
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI(
    title="MicroBank Core & Automated Billing Ecosystem", 
    version="2026.1.0",
    docs_url=None,       # تكتيك السينيور: تعطيل السواجر الافتراضي كلياً لمنع التضارب
    redoc_url=None       # تعطيل الـ Redoc لتأمين المعمار
)
security_scheme = HTTPBearer()

SECRET_KEY = "SUPER_SECRET_BANK_KEY_2026"
ALGORITHM = "HS256"

# Pure Cloud Production Dynamic Injection Layer
def get_db_connection():
    # بتقرأ الـ Value الجاهز والمصلح الـ في الـ Render تلقائياً وبدون أي تداخل
    db_url = os.environ.get("DATABASE_URL")
    return psycopg2.connect(db_url)

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

# [ADDED]: مصفوفات بيانات بوابة الفواتير الجديدة عيار 24
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

# [FIXED PROPERLY]: Explicit indexing database mappings for Deposit Operations
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
        return {
            "status": "Success", 
            "message": f"Successfully deposited {payload.amount} SDG into Account {payload.account_id}"
        }
    except Exception as e:
        if connection: connection.rollback()
        raise HTTPException(status_code=500, detail=f"Deposit Operation Core Failure: {str(e)}")
    finally:
        if connection: connection.close()

@app.post("/login")
def login(payload: UserLogin):
    if payload.account_id == 1 and payload.password == "gorashi":
        token_payload = {"account_id": payload.account_id, "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=15)}
        token = jwt.encode(token_payload, SECRET_KEY, algorithm=ALGORITHM)
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid banking authentication credentials")

# [FIXED PROPERLY]: Explicit Tuple Row Mappings for Balance Auditing
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
            
        return {
            "account_id": int(account[0]), 
            "name": str(account[1]), 
            "balance": float(account[2])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ledger Balance Matrix Failure: {str(e)}")
    finally:
        if connection: connection.close()

# [FIXED PROPERLY]: Explicit Row Matrix Updates for Secured Asset Transfers
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
        if connection: connection.rollback()
        raise HTTPException(status_code=500, detail=f"Transaction voided via rollback: {str(e)}")
    finally:
        if connection: connection.close()

# =========================================================================
# 🏛️ [ADDED]: بوابة الفواتير الرقمية والـ Automated Billing ونظام آفاق المالي
# =========================================================================

# 1. بوابة الاِستعلام عن الفواتير الـمـعـلّـقـة للـ عـمـيـل
@app.get("/invoices/pending/{account_id}", tags=["Automated Invoicing Gateway"])
def get_pending_invoices(account_id: int, token_data: dict = Depends(verify_token)):
    if account_id != token_data.get("account_id"):
        raise HTTPException(status_code=403, detail="Unauthorized invoice mutation scope")
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        # جلب الفواتير المعلقة الخاصة برقم الحساب
        cursor.execute(
            "SELECT bill_number, biller_name, amount, status FROM Invoices WHERE account_id = %s AND status = 'Pending';", 
            (account_id,)
        )
        invoices = cursor.fetchall()
        cursor.close()
        
        result = []
        for inv in invoices:
            result.append({
                "bill_number": str(inv[0]),
                "biller_name": str(inv[1]),
                "amount": float(inv[2]),
                "status": str(inv[3])
            })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Billing ledger audit failure: {str(e)}")
    finally:
        if connection: connection.close()

# 2. بوابة دفع الـفاتورة الـمأمنة بـالـجنـزير بـتكتيك الـ FOR UPDATE السيبراني
@app.post("/invoices/pay", tags=["Automated Invoicing Gateway"])
def execute_invoice_payment(payload: PayInvoicePayload, token_data: dict = Depends(verify_token)):
    if payload.account_id != token_data.get("account_id"):
        raise HTTPException(status_code=403, detail="Unauthorized transaction payload mutation scope")
    
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # تكتيك السينيور الفولاذي: قفل سطر الفاتورة فوراً في الداتابيز لمنع التلاعب المزدوج
        cursor.execute("SELECT biller_name, amount, status FROM Invoices WHERE bill_number = %s FOR UPDATE;", (payload.bill_number,))
        invoice = cursor.fetchone()
        
        if not invoice:
            raise HTTPException(status_code=404, detail="Target billing routing node not found")
        if str(invoice[2]) == "Paid":
            raise HTTPException(status_code=400, detail="Invoice has already been settled and audited")
            
        biller_name = str(invoice[0])
        bill_amount = float(invoice[1])
        
        # قفل سطر رصيد حساب العميل فوراً لمنع السحب المزدوج في نفس الأجزاء من الثانية
        cursor.execute("SELECT balance FROM Accounts WHERE account_id = %s FOR UPDATE;", (payload.account_id,))
        account = cursor.fetchone()
        
        if not account or float(account[0]) < bill_amount:
            raise HTTPException(status_code=400, detail="Insufficient capital deployment assets for billing settlement")
            
        # تنفيذ الخصم البنكي الذري وتحويل الكاش وإغلاق الفاتورة
        cursor.execute("UPDATE Accounts SET balance = balance - %s WHERE account_id = %s;", (bill_amount, payload.account_id))
        cursor.execute("UPDATE Invoices SET status = 'Paid' WHERE bill_number = %s;", (payload.bill_number,))
        
        connection.commit() # بصم العملية خرسانة مسلحة لايف جوة السحاب
        cursor.close()
        
        return {
            "status": "Success",
            "message": f"Successfully settled {biller_name} bill (Ref: {payload.bill_number})",
            "amount_paid": bill_amount
        }
    except Exception as e:
        if connection: connection.rollback() # إلغاء العملية فوراً لو حصل أي مطب أمني أو تقني
        raise HTTPException(status_code=500, detail=f"Billing transaction voided via rollback: {str(e)}")
    finally:
        if connection: connection.close()

        from fastapi.responses import HTMLResponse

# [HACK]: حقن ستارة صفحة الدخول المعزولة الفخمة جوة واجهة الـ Swagger لايف
@app.get("/docs", include_in_schema=False)
def custom_swagger_ui():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MicroBank Core - Secure Secure Login</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://jsdelivr.net">
        <style>
            body { margin: 0; padding: 0; background: #f4f6f9; font-family: sans-serif; }
            #auth-overlay { position: fixed; top:0; left:0; width:100%; height:100%; background:#1a233a; display:flex; justify-content:center; align-items:center; z-index:9999; }
            .login-box { background:#white; padding:40px; border-radius:12px; box-shadow:0 10px 25px rgba(0,0,0,0.3); text-align:center; width:350px; }
            .login-box h2 { color:#1a233a; margin-bottom:25px; font-weight:bold; }
            .login-box input { width:100%; padding:12px; margin-bottom:15px; border:1px solid #ccc; border-radius:6px; box-sizing:border-box; font-size:16px; }
            .login-box button { width:100%; padding:12px; background:#10b981; border:none; color:white; font-size:16px; font-weight:bold; border-radius:6px; cursor:pointer; }
            .login-box button:hover { background:#059669; }
        </style>
    </head>
    <body>
        <!-- شاشة القفل والستارة المعزولة -->
        <div id="auth-overlay">
            <div class="login-box">
                <h2>🏛️ MicroBank Core</h2>
                <input type="number" id="acc_id" placeholder="Account ID (e.g. 1)">
                <input type="password" id="pass" placeholder="Banking Password">
                <button onclick="unlockGateway()">Secure Login</button>
            </div>
        </div>

        <div id="swagger-ui"></div>

        <script src="https://jsdelivr.net"></script>
        <script>
            // كود الجافاسكريبت السينيور المخفي لفتح البوابات ديناميكياً
            function unlockGateway() {
                const accId = document.getElementById('acc_id').value;
                const password = document.getElementById('pass').value;
                
                if(accId == "1" && password == "gorashi") {
                    document.getElementById('auth-overlay').style.display = 'none';
                    // تشغيل السواجر وبناء البوابات تلقائياً بمجرد البصمة بالصّاح
                    const ui = SwaggerUIBundle({
                        url: '/openapi.json',
                        dom_id: '#swagger-ui',
                        deepLinking: true,
                        presets: [SwaggerUIBundle.presets.apis],
                        layout: "BaseLayout"
                    });
                } else {
                    alert("Invalid banking authentication credentials!");
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)