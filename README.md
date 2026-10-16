# 🏦 Financial Microservices Ecosystem & Core Ledger Engine (v2026)

Welcome to the **Financial Microservices Ecosystem**, an enterprise-grade, high-performance, and cryptographically secured financial ledger infrastructure engineered using **Python (FastAPI)** and **PostgreSQL**. This production-ready system is designed to simulate cutting-edge FinTech operations, split into distinct modular ledger kernels handling core retail banking mutations and dynamic time-based automated subscription collection routines.

---

## 🛠️ System Architecture & Core Core Components

### 🏛️ 1. MicroBank Core API Layer
Manages high-velocity retail ledger mutations, user account states, and atomic balance sheets.
* **Negative Balance Prevention:** Enforces database-level constraint matrices (`CHECK balance >= 0.00`) guaranteeing total data integrity against negative balance overflows.
* **Atomic Ledger Mutations:** Utilizing real-time automated **PostgreSQL Triggers & Functions**, instantly auditing and synchronizing transaction payloads across independent customer ledgers in milliseconds.
* **SQL Injection Countermeasures:** Built strictly via **Parameterized Server-Side Queries (`%s`)** neutralizing string-interpolation exploits and continuous runtime data leakage vectors.
* **Transaction Safe-Guards:** Encapsulated within strict explicit execution try-except blocks coupled with immediate state **`rollback` mechanisms** to prevent multi-table corrupted splits.

### ⏰ 2. Automated Smart Billing & Invoicing Engine
An independent automated micro-ledger processing subscription engines and dynamic time-based resource allocations.
* **Automated Time Engine:** Powered by a decentralized background **`APScheduler` cron-job network**, scanning active global accounts, calculating real-time bill schemas, and collecting payments autonomously.
* **Fail-Safe Debt Allocation:** Automatically intercepts accounts short on liquid capital, dropping strict multi-table payment failures and re-routing the status matrix to `Overdue`.
* **Central Collections Routing:** Successfully processes payment clearing into dedicated enterprise virtual settlement ledgers (`Account 999`) with zero runtime overhead.

### 🔐 3. Security Command & Identity Protocols
* **Cryptographic Data Hashing:** Leverages native production **`bcrypt` byte-array encryption algorithms** to process and lock away database login credentials behind immutable salted hashes.
* **Stateless Bearer Tokens (JWT):** Generates securely signed **JSON Web Tokens (HS256)** packed with atomic metadata expiration payloads (15-Minute windows) to authorize high-value API request footprints securely.

---

## 🌐 Dynamic Live Endpoint Footprint

* `GET /` ➔ System Status and Handshake Metrics.
* `GET /balance/{account_id}` ➔ Parameterized secure balance audit tracking.
* `POST /transfer` ➔ High-velocity, atomic multi-account ledger routing.
* `POST /login` ➔ Secure credential matching and stateless JWT transmission.
* `GET /invoices/{account_id}` ➔ Fetches real-time pending recurring bills.
* `POST /invoices/pay/{invoice_id}` ➔ Manual override payment settlement execution.
*
