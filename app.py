from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
import uvicorn
import jwt
import bcrypt
from datetime import datetime, timedelta

# =====================================================================
# 🔐 1. عصب الأمن السيبراني والتشفير الحديث بالـ bcrypt الصافي (بدون passlib)
# =====================================================================

# 🔑 الصق المفتاح السري الأسطوري الطلع ليك من بايثون هنا بين القوسين
SECRET_KEY = "02b02cca03dd2c7df6b3bb99712a984f93e303a90948a8ef9c6f01c3738fbe60"
ALGORITHM = "HS256"

# 🏛️ دالة التشفير الحديثة (تحويل البأسورد لطلاسم مأمنة)
def hash_password(password: str):
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

# 🏛️ dالة مطابقة البأسورد الفولاذية والمحمية ضد كل أخطاء الـ 72 بايت
def verify_password(plain_password: str, hashed_password: str):
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

# 🏛️ dالة توليد كروت تذاكر الأمان الرقمية (JWT)
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# =====================================================================
# 🏛️ 2. واجهة الـ API وصناديق الشحن الذكية (Data Models)
# =====================================================================

app = FastAPI(title="MicroBank Secure Web API", version="2026")

class TransferRequest(BaseModel):
    from_account: int
    to_account: int
    amount: float

class LoginRequest(BaseModel):
    account_id: int
    password_text: str

# 🗄️ دالة فتح الاتصال بالخزنة بأمان تحت الأرض
def get_db_connection():
    connection = psycopg2.connect(
        database="microbank_db",
        user="postgres",
        password="gorashi",  # الباسوورد الحقيقية حقتك
        host="127.0.0.1",
        port="5432"
    )
    return connection

# =====================================================================
# 🌐 3. روابط وبوابات الإنترنت الحية (Endpoints)
# =====================================================================

@app.get("/")
def welcome():
    return {"status": "Active", "system": "MicroBank Core Web API", "engineer": "Qanass Al-Malayin"}

@app.get("/balance/{account_id}")
def view_balance(account_id: int):
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = "SELECT Accounts.account_id, Customers.full_name, Accounts.balance FROM Accounts INNER JOIN Customers ON Accounts.customer_id = Customers.customer_id WHERE Accounts.account_id = %s;"
        cursor.execute(query, (account_id,))
        account_info = cursor.fetchone()
        if account_info is None:
            return {"error": f"Account ID {account_id} does not exist!"}
        return {"status": "Success", "account_id": account_info[0], "customer_name": account_info[1], "balance_sdg": float(account_info[2])}
    except Exception as error:
        return {"error": f"Database Error: {error}"}
    finally:
        if cursor: cursor.close()
        if connection: connection.close()

@app.post("/transfer")
def make_transfer(request: TransferRequest):
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT balance FROM Accounts WHERE account_id = %s;", (request.from_account,))
        sender_res = cursor.fetchone()
        if sender_res is None:
            return {"error": f"Sender Account ID {request.from_account} does not exist!"}
        current_balance = float(sender_res[0])
        if request.amount > current_balance:
            return {"error": "Transaction Denied! Insufficient balance."}
        cursor.execute("SELECT account_id FROM Accounts WHERE account_id = %s;", (request.to_account,))
        receiver_res = cursor.fetchone()
        if receiver_res is None:
            return {"error": f"Target Account ID {request.to_account} does not exist! Transfer blocked."}
        query = "INSERT INTO Transactions (from_account_id, to_account_id, transaction_type, amount) VALUES (%s, %s, 'Transfer', %s);"
        cursor.execute(query, (request.from_account, request.to_account, request.amount))
        connection.commit()
        return {"status": "Success", "message": f"Successfully transferred {request.amount} SDG!"}
    except Exception as error:
        if connection: connection.rollback()
        return {"error": f"Database Error: {error}"}
    finally:
        if cursor: cursor.close()
        if connection: connection.close()

# 🌐 5. التقفيلة الذكية لليلة: بوابة تسجيل الدخول المأمنة وتوليد الـ JWT لايف
@app.post("/login")
def login(request: LoginRequest):
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # 1️⃣ فحص وجود الحساب في الخزنة أولاً
        query = "SELECT account_id FROM Accounts WHERE account_id = %s;"
        cursor.execute(query, (request.account_id,))
        account = cursor.fetchone()
        
        # لو الحساب وهمي وما مسجل في البنك، اِطرد الحرامي طوالي!
        if account is None:
            return {"error": "Invalid Account ID or Password!"}
            
        db_account_id = account[0]
        
        # 🚨 2️⃣ المحك الأمني الذكي لليلة:
        # لو كتب أي باسوورد غلط غير "12345"، السيستم حـ يطرده طوالي بعين حمراء!
        if request.password_text != "12345":
            return {"error": "Invalid Account ID or Password!"}
            
        # 3️⃣ إذا كتب البأسورد الصح "12345"، ولّد تذكرة الأمان الرقمية (JWT) واِقذفها لايف!
        access_token = create_access_token(data={"sub": str(db_account_id)})
        
        return {
            "status": "Success",
            "message": "Access Granted! Welcome to MicroBank Mobile",
            "token_type": "bearer",
            "access_token": access_token  # التذكرة الفولاذية الطايرة في الإنترنت!
        }
    except Exception as error:
        return {"error": f"Database Error: {error}"}
    finally:
        if cursor: cursor.close()
        if connection: connection.close()

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8001, reload=True)
