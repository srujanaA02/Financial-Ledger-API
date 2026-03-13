# 💰 Financial Ledger API

A production-grade **double-entry bookkeeping** REST API built with **FastAPI** and **PostgreSQL**. Designed as the backend for a mock banking application with absolute data integrity, immutability, and auditability.

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Database | PostgreSQL 18 |
| ORM | SQLAlchemy 2.0 |
| Validation | Pydantic V2 |
| Server | Uvicorn |
| Testing | Pytest + HTTPX |
| Containerization | Docker + Docker Compose |

---

## ✨ Features

- ✅ **Double-entry bookkeeping** — every transaction creates a balanced debit + credit pair
- ✅ **ACID transactions** — atomic commits via PostgreSQL
- ✅ **Immutable ledger** — entries are append-only and can never be modified or deleted
- ✅ **Overdraft prevention** — any transaction causing a negative balance is rejected and rolled back
- ✅ **Balance from ledger sum** — balance is always calculated dynamically, never stored
- ✅ **REPEATABLE READ isolation** — prevents race conditions during concurrent transfers
- ✅ **Paginated ledger** — with entry type filtering (debit/credit)
- ✅ **API versioning** — all endpoints served under `/api/v1`
- ✅ **Health check endpoint**
- ✅ **Interactive Swagger UI** at `/docs`

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL 18
- Git

---

### Step 1: Clone the repository
```bash
git clone https://github.com/srujanaA02/financial-ledger-api.git
cd financial-ledger-api
```

---

### Step 2: Create virtual environment
```bash
python -m venv venv

# Activate on Windows (Git Bash)
source venv/Scripts/activate

# Activate on macOS/Linux
source venv/bin/activate
```

---

### Step 3: Install dependencies
```bash
pip install -r requirements.txt
```

---

### Step 4: Setup PostgreSQL Database

Open PostgreSQL shell:
```bash
psql -U postgres -p 5432
```

Run these commands inside psql:
```sql
-- Set postgres password
ALTER USER postgres WITH PASSWORD 'postgres';

-- Create the database
CREATE DATABASE financial_ledger;

-- Create a dedicated user
CREATE USER ledger_user WITH PASSWORD 'ledger_pass';

-- Grant basic privileges
GRANT ALL PRIVILEGES ON DATABASE financial_ledger TO ledger_user;

-- Set database owner
ALTER DATABASE financial_ledger OWNER TO ledger_user;

-- Connect to the new database
\c financial_ledger

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO ledger_user;
ALTER SCHEMA public OWNER TO ledger_user;

-- Verify the database was created
\l

-- Exit psql
\q
```

Verify the connection works:
```bash
psql -U ledger_user -d financial_ledger -p 5432
# Enter password: ledger_pass
# You should see: financial_ledger=>
\q
```

---

### Step 5: Configure environment
```bash
cp .env.example .env
```

Your `.env` file should contain:
```
DATABASE_URL=postgresql://ledger_user:ledger_pass@localhost:5432/financial_ledger
```

---

### Step 6: Run the server
```bash
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Root info |
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/accounts` | Create a new account |
| `GET` | `/api/v1/accounts/{id}` | Get account details + live balance |
| `GET` | `/api/v1/accounts/{id}/ledger` | Get paginated ledger entries |
| `POST` | `/api/v1/deposits` | Deposit funds into an account |
| `POST` | `/api/v1/transfers` | Transfer funds between two accounts |
| `POST` | `/api/v1/withdrawals` | Withdraw funds from an account |

---

## 🖥️ Testing via Swagger UI

1. Start the server: `uvicorn app.main:app --reload`
2. Open browser: **http://127.0.0.1:8000/docs**
3. Follow these steps **in order**:

---

### 1️⃣ Create Account A
- Click **POST /api/v1/accounts** → Click **Try it out** → Paste body → Click **Execute**
```json
{
  "user_id": "user1",
  "account_type": "checking",
  "currency": "USD"
}
```
📋 Copy the `id` from the response — this is your **ACCOUNT_A_ID**

---

### 2️⃣ Create Account B
- Click **POST /api/v1/accounts** → Click **Try it out** → Paste body → Click **Execute**
```json
{
  "user_id": "user2",
  "account_type": "savings",
  "currency": "USD"
}
```
📋 Copy the `id` from the response — this is your **ACCOUNT_B_ID**

---

### 3️⃣ Deposit $1000 into Account A
- Click **POST /api/v1/deposits** → Click **Try it out** → Paste body → Click **Execute**
```json
{
  "account_id": "ACCOUNT_A_ID",
  "amount": 1000,
  "currency": "USD",
  "description": "Initial deposit"
}
```
✅ Response should show `"status": "completed"`

---

### 4️⃣ Check Account A Balance
- Click **GET /api/v1/accounts/{accountId}** → Click **Try it out**
- Enter your **ACCOUNT_A_ID** → Click **Execute**

✅ Response should show `"balance": "1000.0000"`

---

### 5️⃣ Transfer $300 from A to B
- Click **POST /api/v1/transfers** → Click **Try it out** → Paste body → Click **Execute**
```json
{
  "source_account_id": "ACCOUNT_A_ID",
  "destination_account_id": "ACCOUNT_B_ID",
  "amount": 300,
  "currency": "USD",
  "description": "Transfer to user2"
}
```
✅ Account A balance should now be **$700**

---

### 6️⃣ Withdraw $100 from Account A
- Click **POST /api/v1/withdrawals** → Click **Try it out** → Paste body → Click **Execute**
```json
{
  "account_id": "ACCOUNT_A_ID",
  "amount": 100,
  "currency": "USD",
  "description": "ATM withdrawal"
}
```
✅ Account A balance should now be **$600**

---

### 7️⃣ View Ledger for Account A
- Click **GET /api/v1/accounts/{accountId}/ledger** → Click **Try it out**
- Enter your **ACCOUNT_A_ID**
- Set `page = 1`, `page_size = 10`
- Optionally set `entry_type = debit` to filter only debits
- Click **Execute**

✅ You should see all ledger entries with timestamps

---

### 8️⃣ Test Insufficient Funds (should FAIL with 422)
- Click **POST /api/v1/transfers** → Click **Try it out** → Paste body → Click **Execute**
```json
{
  "source_account_id": "ACCOUNT_A_ID",
  "destination_account_id": "ACCOUNT_B_ID",
  "amount": 99999,
  "currency": "USD",
  "description": "This should fail"
}
```
✅ Response: **HTTP 422**
```json
{
  "detail": "Insufficient funds"
}
```

---

### 9️⃣ Check Health
- Click **GET /health** → Click **Try it out** → Click **Execute**
```json
{
  "status": "healthy",
  "uptime_seconds": 120.5,
  "version": "1.0.0",
  "database": "connected"
}
```

---

## 💻 Testing via curl (Git Bash)

> Replace `ACCOUNT_A_ID` and `ACCOUNT_B_ID` with the actual UUIDs from your responses.

---

### Health Check
```bash
curl http://localhost:8000/health
```

---

### Create Account A
```bash
curl -X POST http://localhost:8000/api/v1/accounts \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user1", "account_type": "checking", "currency": "USD"}'
```

---

### Create Account B
```bash
curl -X POST http://localhost:8000/api/v1/accounts \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user2", "account_type": "savings", "currency": "USD"}'
```

---

### Get Account Details (with live balance)
```bash
curl http://localhost:8000/api/v1/accounts/ACCOUNT_A_ID
```

---

### Deposit $1000 into Account A
```bash
curl -X POST http://localhost:8000/api/v1/deposits \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "ACCOUNT_A_ID",
    "amount": 1000,
    "currency": "USD",
    "description": "Initial deposit"
  }'
```

---

### Transfer $300 from Account A to Account B
```bash
curl -X POST http://localhost:8000/api/v1/transfers \
  -H "Content-Type: application/json" \
  -d '{
    "source_account_id": "ACCOUNT_A_ID",
    "destination_account_id": "ACCOUNT_B_ID",
    "amount": 300,
    "currency": "USD",
    "description": "Transfer to user2"
  }'
```

---

### Withdraw $100 from Account A
```bash
curl -X POST http://localhost:8000/api/v1/withdrawals \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "ACCOUNT_A_ID",
    "amount": 100,
    "currency": "USD",
    "description": "ATM withdrawal"
  }'
```

---

### Get Ledger — All Entries (paginated)
```bash
curl "http://localhost:8000/api/v1/accounts/ACCOUNT_A_ID/ledger?page=1&page_size=10"
```

### Get Ledger — Filter by Debit Only
```bash
curl "http://localhost:8000/api/v1/accounts/ACCOUNT_A_ID/ledger?page=1&page_size=10&entry_type=debit"
```

### Get Ledger — Filter by Credit Only
```bash
curl "http://localhost:8000/api/v1/accounts/ACCOUNT_A_ID/ledger?page=1&page_size=10&entry_type=credit"
```

---

### Test Insufficient Funds (should return 422)
```bash
curl -X POST http://localhost:8000/api/v1/transfers \
  -H "Content-Type: application/json" \
  -d '{
    "source_account_id": "ACCOUNT_A_ID",
    "destination_account_id": "ACCOUNT_B_ID",
    "amount": 99999
  }'
```
Expected:
```json
{"detail": "Insufficient funds"}
```

---

### Test Negative Amount (should return 400)
```bash
curl -X POST http://localhost:8000/api/v1/deposits \
  -H "Content-Type: application/json" \
  -d '{"account_id": "ACCOUNT_A_ID", "amount": -100}'
```
Expected:
```json
{"detail": "Amount must be positive"}
```

---

## 🐳 Docker Setup

Make sure **Docker Desktop** is running, then:

```bash
# Build and start all services
docker-compose up --build

# Run in background (detached mode)
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Stop and remove volumes (clears database)
docker-compose down -v
```

Services started:
- **PostgreSQL** → `localhost:5433`
- **FastAPI** → `localhost:8000`

Visit: **http://localhost:8000/docs**

---

## 🧪 Running Tests

```bash
# Run all tests with verbose output
pytest tests/ -v

# Run only account tests
pytest tests/test_accounts.py -v

# Run only transaction tests
pytest tests/test_transactions.py -v

# Run a specific single test
pytest tests/test_transactions.py::test_transfer_insufficient_funds -v

# Run with short summary
pytest tests/ -v --tb=short
```

Expected output:
```
tests/test_accounts.py::test_create_account PASSED
tests/test_accounts.py::test_get_account PASSED
tests/test_accounts.py::test_get_account_not_found PASSED
tests/test_accounts.py::test_get_ledger_empty PASSED
tests/test_accounts.py::test_get_ledger_pagination PASSED
tests/test_accounts.py::test_get_ledger_filter_by_entry_type PASSED
tests/test_transactions.py::test_deposit PASSED
tests/test_transactions.py::test_deposit_updates_balance PASSED
tests/test_transactions.py::test_deposit_negative_amount PASSED
tests/test_transactions.py::test_transfer_success PASSED
tests/test_transactions.py::test_transfer_updates_both_balances PASSED
tests/test_transactions.py::test_transfer_insufficient_funds PASSED
tests/test_transactions.py::test_transfer_source_not_found PASSED
tests/test_transactions.py::test_withdrawal_success PASSED
tests/test_transactions.py::test_double_entry_creates_two_ledger_entries PASSED

================ 15 passed in 1.5s ================
```

---

## 📮 Postman Collection

1. Open **Postman**
2. Click **Import**
3. Select `postman_collection.json` from the project root
4. Run requests **in order** from top to bottom
5. Account IDs are **automatically saved** as variables between requests

---

## 📊 Double-Entry Bookkeeping Explained

Every financial operation creates **two balanced ledger entries**.

### Deposit $1000
```
CREDIT  user_account    +$1000   (money received)
DEBIT   system_account  -$1000   (source of funds)
```

### Transfer $300 from A → B
```
DEBIT   account_A  -$300   (money out)
CREDIT  account_B  +$300   (money in)
```

> The sum of all entries for a transaction always equals **zero** — the core principle of double-entry bookkeeping.

---

## 🗄️ Database Schema

```
┌─────────────────────┐     ┌──────────────────────┐     ┌──────────────────────────┐
│      accounts       │     │     transactions      │     │      ledger_entries      │
├─────────────────────┤     ├──────────────────────┤     ├──────────────────────────┤
│ id (UUID) PK        │◄────│ source_account_id FK │     │ id (UUID) PK             │
│ user_id             │◄────│ dest_account_id FK   │◄────│ account_id FK            │
│ account_type        │     │ id (UUID) PK         │◄────│ transaction_id FK        │
│ currency            │     │ transaction_type     │     │ entry_type (debit/credit) │
│ status              │     │ amount               │     │ amount                   │
│ created_at          │     │ currency             │     │ timestamp                │
└─────────────────────┘     │ status               │     └──────────────────────────┘
                            │ description          │
                            │ created_at           │
                            └──────────────────────┘
```

---

## 🔒 Business Rules

| Rule | HTTP Status | Message |
|---|---|---|
| Insufficient funds | 422 | `Insufficient funds` |
| Frozen account | 422 | `Account is frozen` |
| Negative amount | 400 | `Amount must be positive` |
| Account not found | 404 | `Account not found` |
| Ledger modification | 500 | `Ledger entries are immutable` |

---

## 📁 Project Structure

```
financial-ledger-api/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── accounts.py         # Account endpoints
│   │       └── transactions.py     # Transaction endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py               # Environment configuration
│   ├── db/
│   │   ├── __init__.py
│   │   └── database.py             # Database connection & session
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py               # SQLAlchemy ORM models
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── schemas.py              # Pydantic request/response schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── account_service.py      # Account business logic
│   │   └── transaction_service.py  # Transaction business logic
│   └── main.py                     # FastAPI app entry point
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # Test fixtures & database setup
│   ├── test_accounts.py            # Account endpoint tests
│   └── test_transactions.py        # Transaction endpoint tests
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env
├── .env.example
├── .gitignore
├── postman_collection.json
├── requirements.txt
└── README.md
```

---

## 🌐 Environment Variables

| Variable | Description | Example |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://ledger_user:ledger_pass@localhost:5432/financial_ledger` |

---
