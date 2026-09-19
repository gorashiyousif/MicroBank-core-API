from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
import uvicorn

app = FastAPI(title="MicroBank Secure Web API", version="2026")

# 📦 صندوق ذكي (Model) لاستقبل البيانات بأمان ومنع التلاعب
class TransferRequest(BaseModel):
    from_account: int
    to_account: int
    amount: float

# 🗄️ دالة فتح الاتصال بالخزنة بأمان
def get_db_connection():
    connection = psycopg2.connect(
        database="microbank_db",
        user="postgres",
        password="gorashi",  # الباسوورد الحقيقية حقتك
        host="127.0.0.1",
        port="5432"
    )
    return connection

@app.get("/")
def welcome():
    return {"status": "Active", "system": "MicroBank Core Web API", "engineer": "Qanass Al-Malayin"}

# 🌐 رابط عرض الرصيد المأمن
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

# 🌐 رابط عرض كشف الحساب التاريخي
@app.get("/history/{account_id}")
def view_history(account_id: int):
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = "SELECT transaction_id, transaction_type, amount, created_at FROM Transactions WHERE from_account_id = %s OR to_account_id = %s ORDER BY created_at DESC;"
        cursor.execute(query, (account_id, account_id))
        rows = cursor.fetchall()
        if not rows:
            return {"account_id": account_id, "message": "No transactions found."}
        history_list = [{"transaction_id": r[0], "type": r[1], "amount_sdg": float(r[2]), "date_time": str(r[3])} for r in rows]
        return {"status": "Success", "account_id": account_id, "history": history_list}
    except Exception as error:
        return {"error": f"Database Error: {error}"}
    finally:
        if cursor: cursor.close()
        if connection: connection.close()

# 🟢 البوابة الذكية للتحويل المالي المأمن ضد الحسابات الوهمية والسالب
@app.post("/transfer")
def make_transfer(request: TransferRequest):
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # 1️⃣ فحص وجود حساب المرسل أولاً ومعرفة رصيده
        cursor.execute("SELECT balance FROM Accounts WHERE account_id = %s;", (request.from_account,))
        sender_res = cursor.fetchone()
        if sender_res is None:
            return {"error": f"Sender Account ID {request.from_account} does not exist!"}
            
        current_balance = float(sender_res[0])
        if request.amount > current_balance:
            return {"error": "Transaction Denied! Insufficient balance."}
            
        # 2️⃣ الفحص الذكي الجديد: التأكد من وجود حساب المستلم في الخزنة قبل التحويل
        cursor.execute("SELECT account_id FROM Accounts WHERE account_id = %s;", (request.to_account,))
        receiver_res = cursor.fetchone()
        if receiver_res is None:
            return {"error": f"Target Account ID {request.to_account} does not exist! Transfer blocked."}
            
        # 3️⃣ إذا الحسابين موجودين والرصيد كافي، نفذ العملية بأمان مية المية
        query = "INSERT INTO Transactions (from_account_id, to_account_id, transaction_type, amount) VALUES (%s, %s, 'Transfer', %s);"
        cursor.execute(query, (request.from_account, request.to_account, request.amount))
        connection.commit()
        
        return {"status": "Success", "message": f"Successfully transferred {request.amount} SDG!"}
        
    except Exception as error:
        if connection: connection.rollback() # التراجع الفوري لو حصل أي انهيار مفاجئ
        return {"error": f"Database Error: {error}"}
    finally:
        if cursor: cursor.close()
        if connection: connection.close()

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)