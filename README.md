# 🏦 MicroBank Core Web API (MVP)

A secure, high-performance Core Banking Backend API developed using modern software architecture standards for financial institutions.

## 🚀 Key Architectural Features
- ** enterprise-Grade DB Architecture:** Designed with robust PostgreSQL constraints, preventing negative balances (`CHECK constraint`) [16.4].
- **Automated Banking Logic:** Implemented secure database `TRIGGERS` to handle funds transfer atomically without manual database interaction issues [16.4].
- **Web API Layer:** Built with **FastAPI** for ultra-fast, asynchronous request handling (`ASGI` standard) [16.4].
- **Production-Level Security:** Fully protected against **SQL Injection** vulnerabilities using parameterized queries (`%s`) and safeguarded against data loss via explicit transaction `ROLLBACK` handling [16.4].
- **Intelligent Error Interception:** Custom validation layers to prevent transactions on non-existent accounts with clean, structured banking feedback [16.4].

## 🛠️ Tech Stack
- **Language:** Python
- **Framework:** FastAPI
- **Database:** PostgreSQL
- **Driver:** Psycopg2
- **Server:** Uvicorn
- **Version Control:** Git & GitHub

## 🌐 Interactive API Documentation (Swagger UI)
The system automatically generates interactive documentation. Once deployed, you can access the comprehensive testing suite at:
`http://localhost:8000/docs`

---
*Developed with excellence by **Engineer: Qanass Al-Malayin** (Senior Financial Backend Engineer).*
