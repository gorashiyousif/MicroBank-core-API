import psycopg2

connection = None
cursor = None

try:
    connection = psycopg2.connect(
        database="microbank_db",
        user="postgres",
        password="gorashi",  # الباسوورد الحقيقية حقتك
        host="127.0.0.1",
        port="5432"
    )
    cursor = connection.cursor()
    
    print("====================================")
    print("   🌐 SECURE MICROBANK SYSTEM 🌐   ")
    print("====================================")
    
    active_account = input("Please enter the Account ID to manage (e.g., 1): ")
    
    # 🛡️ التأمين 1: استخدام %s بيمنع الـ SQL Injection تماماً وبيفصل البيانات عن كود السيرفر!
    cursor.execute("SELECT Accounts.account_id, Customers.full_name FROM Accounts INNER JOIN Customers ON Accounts.customer_id = Customers.customer_id WHERE Accounts.account_id = %s;", (active_account,))
    account_info = cursor.fetchone()
    
    if account_info is None:
        print(f"\n❌ Error: Account ID {active_account} does not exist!")
    else:
        customer_name = account_info
        print(f"\n✨ Access Granted! Managing account for: {customer_name} ✨")
        
        while True:
            print("\n====================================")
            print(f"   🏦 MANAGING ACCOUNT ID: {active_account} ({customer_name})")
            print("====================================")
            print("1. View Account Balance")
            print("2. Deposit Money")
            print("3. Withdraw Money")
            print("4. Transfer Money")
            print("5. View Transaction History 📄")
            print("6. Exit System 🚫")
            print("====================================")
            
            choice = input("Enter choice number (1-6): ")
            
            if choice == "1":
                cursor.execute("SELECT balance FROM Accounts WHERE account_id = %s;", (active_account,))
                balance = cursor.fetchone()
                print(f"\n✅ Balance: {balance} SDG")
                
            elif choice == "2":
                amount = float(input("Enter deposit amount: "))
                # التمرير الآمن بالـ %s والـ كرتونة المنفصلة التحت
                cursor.execute("UPDATE Accounts SET balance = balance + %s WHERE account_id = %s;", (amount, active_account))
                cursor.execute("INSERT INTO Transactions (from_account_id, to_account_id, transaction_type, amount) VALUES (%s, %s, 'Deposit', %s);", (active_account, active_account, amount))
                connection.commit() 
                print(f"\n💵 Successfully deposited {amount} SDG!")
                
            elif choice == "3":
                cursor.execute("SELECT balance FROM Accounts WHERE account_id = %s;", (active_account,))
                current_balance = float(cursor.fetchone())
                amount = float(input("Enter withdraw amount: "))
                
                if amount > current_balance:
                    print(f"\n❌ Transaction Denied! Insufficient balance.")
                else:
                    cursor.execute("UPDATE Accounts SET balance = balance - %s WHERE account_id = %s;", (amount, active_account))
                    cursor.execute("INSERT INTO Transactions (from_account_id, to_account_id, transaction_type, amount) VALUES (%s, %s, 'Withdraw', %s);", (active_account, active_account, amount))
                    connection.commit()
                    print(f"\n💸 Successfully withdrew {amount} SDG!")
                
            elif choice == "4":
                cursor.execute("SELECT balance FROM Accounts WHERE account_id = %s;", (active_account,))
                current_balance = float(cursor.fetchone())
                to_account = input("Enter target Account ID: ")
                amount = float(input("Enter transfer amount: "))
                
                if amount > current_balance:
                    print(f"\n❌ Transaction Denied! Insufficient balance.")
                else:
                    cursor.execute("INSERT INTO Transactions (from_account_id, to_account_id, transaction_type, amount) VALUES (%s, %s, 'Transfer', %s);", (active_account, to_account, amount))
                    connection.commit()
                    print(f"\n🚀 Successfully transferred {amount} SDG to Account ID {to_account}!")
                    
            elif choice == "5":
                print(f"\n--- TRANSACTION HISTORY FOR ACCOUNT {active_account} ---")
                cursor.execute("SELECT transaction_id, transaction_type, amount, created_at FROM Transactions WHERE from_account_id = %s OR to_account_id = %s ORDER BY created_at DESC;", (active_account, active_account))
                rows = cursor.fetchall()
                
                if not rows:
                    print("No transactions found for this account.")
                else:
                    for row in rows:
                        print(f"ID: {row} | Type: {row} | Amount: {row} SDG | Date: {row}")
                print("--------------------------------------------------")
                
            elif choice == "6":
                print("\n👋 Thank you for using MicroBank. Goodbye, Engineer!\n")
                break
            else:
                print("\n❌ Invalid choice! Please select 1 to 6.")

except Exception as error:
    # 🛡️ التأمين 2: لو حصل أي خطأ أو فصلت الكهرباء في نص الطيران، امسح كل الحركات المعلقة فوراً ورجع القروش مكانه!
    if connection:
        connection.rollback() [16.4]
    print(f"Database Error: {error}")

finally:
    # قفل الموظف والبوابة بـ أمان تحت أي ظرف
    if cursor:
        cursor.close()
    if connection:
        connection.close()