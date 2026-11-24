# 🏦 MicroBank Core, Automated Billing & Real-Time AML RegTech Ecosystem

A production-grade FinTech backend engine built with **Python (FastAPI)** and **PostgreSQL (Neon Cloud)**, combining 10+ years of retail banking operations and compliance domain expertise with modern microservices architecture.

## 🚀 Core Modules & Architecture

### 1. Core Banking Ledger (`Account & Transfer Engine`)
- **ACID-Compliant Transactions:** Enforces strict atomicity (`commit`/`rollback`) to guarantee zero capital loss during peer-to-peer transfers and deposits.
- **Concurrency Control:** Utilizes PostgreSQL row-level locking (`SELECT ... FOR UPDATE`) to eliminate race conditions and prevent double-spending.
- **Stateless Security:** Protected via **JWT (JSON Web Tokens)** with strict scope validation ensuring users only mutate authorized accounts.

### 2. Automated Recurring Billing Gateway (`Invoicing Microservice`)
- **Real-Time Bill Settlement:** Fetches pending telecom/utility invoices (`GET /invoices/pending/{account_id}`) and executes atomic balance deductions (`POST /invoices/pay`) with instant status reconciliation.

### 3. Real-Time Fraud & AML Screening Engine (`RegTech Compliance`)
- **Pre-Transaction Interception:** Every transfer passes through an automated compliance checkpoint before ledger execution:
  - **Blacklist Screening:** Instantly blocks transfers to sanctioned/high-risk entities (`HTTP 403 AML Compliance Block`).
  - **High-Value Threshold Monitoring:** Flags transactions exceeding `20,000 SDG` for compliance review.
  - **Audit & Compliance Ledger:** Logs all blocked/flagged attempts with timestamps in `aml_alerts` (`GET /aml/alerts`).

## 🛠️ Tech Stack
- **Backend Framework:** Python 3, FastAPI, Pydantic, Uvicorn
- **Database:** Cloud PostgreSQL (Neon.tech), `psycopg2`
- **Security:** JWT (`PyJWT`), HTTPBearer
- **Deployment:** Render Cloud Web Services (CI/CD via GitHub)
-
