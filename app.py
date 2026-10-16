from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
import uvicorn
import jwt
import bcrypt
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
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

# ⏰ دالة الأتمتة الذكية: بتشتغل ورا الكواليس وتفحص وتخصم الفواتير تلقائياً بالوقت
def auto_billing_job():
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # 1. نفتش عن الفواتير الـ غير مدفوعة (Unpaid أو Overdue) وحان وقت سدادها
        query = "SELECT invoice_id FROM Invoices WHERE status IN ('Unpaid', 'Overdue') AND next_payment_date <= NOW();"
        cursor.execute(query)
        unpaid_invoices = cursor.fetchall()
        
        # 2. نلف على الفواتير دي فاتورة فاتورة ونطير نخصمها لايف!
        for inv in unpaid_invoices:
            inv_id = inv[0]
            print(f"⏰ [Auto-Billing] Found pending invoice ID {inv_id}. Processing automated debit...")
            # بنستدعي نفس دالة الدفع الـ كتبناها قبيل عشان تخلص الخصم بأمان ملوكي
            process_invoice_payment(invoice_id=inv_id)
            
    except Exception as error:
        print(f"⏰ [Auto-Billing Error] {error}")
    finally:
        if cursor: cursor.close()
        if connection: connection.close()

# 🚦 تشغيل وإطلاق محرك الوقت التلقائي (Background Scheduler) جوة السيرفر
scheduler = BackgroundScheduler()
# بنخلي المحرك يصحى براهو (كل 1 دقيقة) وينفذ دالة الفحص والخصم الأوتوماتيكي
scheduler.add_job(auto_billing_job, 'interval', minutes=1)
scheduler.start()



# 🌐 بوابة الدفع الحية: معالجة ودفع الفاتورة يدوياً وخصمها من البنك
@app.post("/invoices/pay/{invoice_id}")
def process_invoice_payment(invoice_id: int):
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # 1️⃣ نسحب بيانات الفاتورة المستهدفة من الخزنة
        cursor.execute("SELECT account_id, billing_amount, status FROM Invoices WHERE invoice_id = %s;", (invoice_id,))
        invoice = cursor.fetchone()
        
        if invoice is None:
            return {"error": f"Invoice ID {invoice_id} does not exist!"}
            
        account_id = invoice[0]
        billing_amount = float(invoice[1])
        status = invoice[2]
        
        # لو الفاتورة مدفوعة ومقفلة أصلاً من قبل كدا
        if status == 'Paid':
            return {"message": f"Invoice {invoice_id} has already been settled and paid."}
            
        # 2️⃣ نطير نـجيب رصيد الحساب البنكي المربوط بالفاتورة دي
        cursor.execute("SELECT balance FROM Accounts WHERE account_id = %s;", (account_id,))
        account_res = cursor.fetchone()
        
        if account_res is None:
            return {"error": f"Linked Bank Account ID {account_id} not found!"}
            
        current_balance = float(account_res[0])
        
        # 🚨 الفحص المالي الصارم: لو القروش ما كافية، اِقفل العملية واِقلبها متأخرة طوالي!
        if billing_amount > current_balance:
            cursor.execute("UPDATE Invoices SET status = 'Overdue' WHERE invoice_id = %s;", (invoice_id,))
            connection.commit()
            return {"error": "Payment Declined: Insufficient balance. Invoice marked as Overdue."}
            
        # 3️⃣ صبّ الخرسانة والعمليات المتتالية جوة عملية مأمنة وموحدة (Atomic Block)
        # خصم قيمة الفاتورة من حساب البنك الأساسي للزبون
        cursor.execute("UPDATE Accounts SET balance = balance - %s WHERE account_id = %s;", (billing_amount, account_id))
        
        # تسجيل العملية جوة جدول المعاملات التاريخي (الرقم 999 بيمثل حساب تحصيل الفواتير الافتراضي)
        cursor.execute(
            "INSERT INTO Transactions (from_account_id, to_account_id, transaction_type, amount) VALUES (%s, %s, 'Bill Payment', %s);",
            (account_id, 999, billing_amount)
        )
        
        # قلب حالة الفاتورة جوة جدول الفواتير لـ مدفوعة بنجاح
        cursor.execute("UPDATE Invoices SET status = 'Paid' WHERE invoice_id = %s;", (invoice_id,))
        
        # تثبيت وحفظ الشغل كلو في القرص بنجاح ملوكي
        connection.commit()
        
        return {
            "status": "Success",
            "message": f"Invoice {invoice_id} successfully paid!",
            "debited_amount_sdg": billing_amount,
            "linked_account": account_id,
            "invoice_new_status": "Paid"
        }
        
    except Exception as error:
        if connection: 
            connection.rollback() # فرملة ومحو أي عملية مكسرة لو حصل طشاش في الشبكة
        return {"error": f"Critical Database Error: {error}"}
    finally:
        if cursor: cursor.close()
        if connection: connection.close()




    # 📦 صندوق ذكي (Model) لعرض بيانات الفواتير بأمان
class InvoiceResponse(BaseModel):
    invoice_id: int
    account_id: int
    billing_amount: float
    status: str
    next_payment_date: datetime

# 🌐 بوابة الإنترنت الجديدة: رابط عرض فواتير العميل لايف من الخزنة
@app.get("/invoices/{account_id}")
def view_customer_invoices(account_id: int):
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # 🛡️ Parameterized Query مأمن مية المية ضد الـ SQL Injection بالـ %s
        query = "SELECT invoice_id, account_id, billing_amount, status, next_payment_date FROM Invoices WHERE account_id = %s;"
        cursor.execute(query, (account_id,))
        rows = cursor.fetchall()
        
        if not rows:
            return {"account_id": account_id, "message": "No recurring invoices found for this account."}
            
        # تحويل الداتا الجاية من الـ Postgres لقائمة JSON منسقة ومفهومة للموبايل
        invoices_list = []
        for r in rows:
            invoices_list.append({
                "invoice_id": r[0],
                "account_id": r[1],
                "billing_amount": float(r[2]),
                "status": r[3],
                "next_payment_date": str(r[4])
            })
            
        return {"status": "Success", "account_id": account_id, "invoices": invoices_list}
        
    except Exception as error:
        return {"error": f"Database Error: {error}"}
    finally:
        if cursor: cursor.close()
        if connection: connection.close()
