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
- PostgreSQL 16+
- Git

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/financial-ledger-api.git
cd financial-ledger-api
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/Scripts/activate  # Windows (Git Bash)
source venv/bin/activate       # macOS/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
# Edit .env with your database credentials
```

### 5. Setup PostgreSQL
```sql
CREATE DATABASE financial_ledger;
CREATE USER ledger_user WITH PASSWORD 'ledger_pass';
GRANT ALL PRIVILEGES ON DATABASE financial_ledger TO ledger_user;
ALTER DATABASE financial_ledger OWNER TO ledger_user;
\c financial_ledger
GRANT ALL ON SCHEMA public TO ledger_user;
ALTER SCHEMA public OWNER TO ledger_user;
```

### 6. Run the server
```bash
uvicorn app.main:app --reload
```

Visit: **http://127.0.0.1:8000/docs**

---

## 🐳 Docker Setup

```bash
docker-compose up --build
```

This will spin up:
- **PostgreSQL** on port `5433`
- **FastAPI** on port `8000`

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

## 📖 Usage Examples

### Create an Account
```bash
curl -X POST http://localhost:8000/api/v1/accounts \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user1", "account_type": "checking", "currency": "USD"}'
```

### Deposit Funds
```bash
curl -X POST http://localhost:8000/api/v1/deposits \
  -H "Content-Type: application/json" \
  -d '{"account_id": "<ACCOUNT_ID>", "amount": 1000, "description": "Initial deposit"}'
```

### Transfer Between Accounts
```bash
curl -X POST http://localhost:8000/api/v1/transfers \
  -H "Content-Type: application/json" \
  -d '{
    "source_account_id": "<ACCOUNT_A_ID>",
    "destination_account_id": "<ACCOUNT_B_ID>",
    "amount": 300,
    "description": "Payment"
  }'
```

### Get Paginated Ledger (filtered by entry type)
```bash
curl "http://localhost:8000/api/v1/accounts/<ACCOUNT_ID>/ledger?page=1&page_size=10&entry_type=credit"
```

---

## 📊 Double-Entry Bookkeeping

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

> The sum of all entries for a transaction always equals **zero** — this is the core principle of double-entry bookkeeping.

---

## 🗄️ Database Schema

```
┌─────────────────────┐     ┌──────────────────────┐     ┌─────────────────────────┐
│      accounts       │     │     transactions      │     │      ledger_entries     │
├─────────────────────┤     ├──────────────────────┤     ├─────────────────────────┤
│ id (UUID) PK        │◄────│ source_account_id FK │     │ id (UUID) PK            │
│ user_id             │◄────│ dest_account_id FK   │◄────│ account_id FK           │
│ account_type        │     │ id (UUID) PK         │◄────│ transaction_id FK       │
│ currency            │     │ transaction_type     │     │ entry_type (debit/credit)│
│ status              │     │ amount               │     │ amount                  │
│ created_at          │     │ currency             │     │ timestamp               │
└─────────────────────┘     │ status               │     └─────────────────────────┘
                            │ description          │
                            │ created_at           │
                            └──────────────────────┘
```

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

### Test Coverage

| Test | Description |
|---|---|
| `test_create_account` | Account creation returns 201 with correct fields |
| `test_get_account` | Account retrieval returns correct data |
| `test_get_account_not_found` | Returns 404 for unknown account |
| `test_get_ledger_empty` | New account has empty ledger |
| `test_get_ledger_pagination` | Pagination works correctly |
| `test_get_ledger_filter_by_entry_type` | Filter by debit/credit works |
| `test_deposit` | Deposit creates completed transaction |
| `test_deposit_updates_balance` | Balance increases after deposit |
| `test_deposit_negative_amount` | Rejects negative amounts with 400 |
| `test_transfer_success` | Transfer completes successfully |
| `test_transfer_updates_both_balances` | Both accounts updated correctly |
| `test_transfer_insufficient_funds` | Rejects with 422 when funds insufficient |
| `test_transfer_source_not_found` | Returns 404 for unknown account |
| `test_withdrawal_success` | Withdrawal completes successfully |
| `test_double_entry_creates_two_ledger_entries` | Verifies debit+credit pair created |

---

## 🔒 Business Rules

| Rule | Behavior |
|---|---|
| Negative balance | Transaction rejected with `422 Unprocessable Entity` |
| Frozen account | Transaction rejected with `422 Unprocessable Entity` |
| Negative amount | Rejected with `400 Bad Request` |
| Account not found | Rejected with `404 Not Found` |
| Ledger modification | Blocked at application level — raises exception |

---

## 📁 Project Structure

```
financial-ledger-api/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── accounts.py        # Account endpoints
│   │       └── transactions.py    # Transaction endpoints
│   ├── core/
│   │   └── config.py              # Environment configuration
│   ├── db/
│   │   └── database.py            # Database connection & session
│   ├── models/
│   │   └── models.py              # SQLAlchemy ORM models
│   ├── schemas/
│   │   └── schemas.py             # Pydantic request/response schemas
│   ├── services/
│   │   ├── account_service.py     # Account business logic
│   │   └── transaction_service.py # Transaction business logic
│   └── main.py                    # FastAPI app entry point
├── tests/
│   ├── conftest.py                # Test fixtures
│   ├── test_accounts.py           # Account tests
│   └── test_transactions.py       # Transaction tests
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.example
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

## 📮 Postman Collection

Import `postman_collection.json` into Postman for a ready-to-use collection with:
- Automated test scripts
- Variable capture (account IDs auto-saved between requests)
- All endpoints pre-configured

---
