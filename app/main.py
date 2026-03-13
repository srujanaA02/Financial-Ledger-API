from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import Base, engine
from app.api.routes import accounts, transactions
import time

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Financial Ledger API",
    description="""
## Double-Entry Bookkeeping System

A robust financial ledger API that implements double-entry bookkeeping principles.

### Features
- ✅ Double-entry bookkeeping (every transaction creates debit + credit)
- ✅ ACID transactions with PostgreSQL
- ✅ Immutable ledger entries (append-only audit trail)
- ✅ Overdraft prevention
- ✅ Balance calculated from ledger sum
- ✅ Concurrent transfer safety with REPEATABLE READ isolation
    """,
    version="1.0.0",
    contact={
        "name": "Financial Ledger API",
        "email": "support@financialledger.com"
    },
    license_info={
        "name": "MIT"
    }
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Versioned routers
app.include_router(accounts.router, prefix="/api/v1")
app.include_router(transactions.router, prefix="/api/v1")

START_TIME = time.time()

@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Financial Ledger API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "version": "1.0.0",
        "database": "connected"
    }