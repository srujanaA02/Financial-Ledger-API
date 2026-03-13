from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.models import Account, Transaction, LedgerEntry, TransactionType, TransactionStatus, EntryType, AccountStatus
from app.schemas.schemas import TransferRequest, DepositRequest, WithdrawalRequest
from app.services.account_service import calculate_balance, get_account
from decimal import Decimal
from fastapi import HTTPException


def set_isolation_level(db: Session):
    """Only set isolation level for PostgreSQL — SQLite doesn't support it."""
    try:
        dialect = db.bind.dialect.name
    except Exception:
        dialect = "unknown"
    if dialect == "postgresql":
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))


def get_or_create_system_account(db: Session) -> Account:
    system = db.query(Account).filter(Account.user_id == "SYSTEM").first()
    if not system:
        from app.models.models import AccountType
        system = Account(
            user_id="SYSTEM",
            account_type=AccountType.checking,
            currency="USD"
        )
        db.add(system)
        db.commit()
        db.refresh(system)
    return system


def execute_transfer(db: Session, data: TransferRequest) -> Transaction:
    set_isolation_level(db)

    source = get_account(db, data.source_account_id)
    dest = get_account(db, data.destination_account_id)

    if not source:
        raise HTTPException(status_code=404, detail="Source account not found")
    if not dest:
        raise HTTPException(status_code=404, detail="Destination account not found")
    if source.status == AccountStatus.frozen:
        raise HTTPException(status_code=422, detail="Source account is frozen")
    if dest.status == AccountStatus.frozen:
        raise HTTPException(status_code=422, detail="Destination account is frozen")
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    source_balance = calculate_balance(db, data.source_account_id)
    if source_balance - data.amount < 0:
        raise HTTPException(status_code=422, detail="Insufficient funds")

    txn = Transaction(
        transaction_type=TransactionType.transfer,
        source_account_id=data.source_account_id,
        destination_account_id=data.destination_account_id,
        amount=data.amount,
        currency=data.currency,
        status=TransactionStatus.pending,
        description=data.description
    )
    db.add(txn)
    db.flush()

    db.add(LedgerEntry(account_id=data.source_account_id, transaction_id=txn.id, entry_type=EntryType.debit, amount=data.amount))
    db.add(LedgerEntry(account_id=data.destination_account_id, transaction_id=txn.id, entry_type=EntryType.credit, amount=data.amount))

    txn.status = TransactionStatus.completed
    db.commit()
    db.refresh(txn)
    return txn


def execute_deposit(db: Session, data: DepositRequest) -> Transaction:
    set_isolation_level(db)

    dest = get_account(db, data.account_id)
    if not dest:
        raise HTTPException(status_code=404, detail="Account not found")
    if dest.status == AccountStatus.frozen:
        raise HTTPException(status_code=422, detail="Account is frozen")
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    system = get_or_create_system_account(db)

    txn = Transaction(
        transaction_type=TransactionType.deposit,
        source_account_id=system.id,
        destination_account_id=data.account_id,
        amount=data.amount,
        currency=data.currency,
        status=TransactionStatus.pending,
        description=data.description
    )
    db.add(txn)
    db.flush()

    db.add(LedgerEntry(account_id=data.account_id, transaction_id=txn.id, entry_type=EntryType.credit, amount=data.amount))

    txn.status = TransactionStatus.completed
    db.commit()
    db.refresh(txn)
    return txn


def execute_withdrawal(db: Session, data: WithdrawalRequest) -> Transaction:
    set_isolation_level(db)

    source = get_account(db, data.account_id)
    if not source:
        raise HTTPException(status_code=404, detail="Account not found")
    if source.status == AccountStatus.frozen:
        raise HTTPException(status_code=422, detail="Account is frozen")
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    balance = calculate_balance(db, data.account_id)
    if balance - data.amount < 0:
        raise HTTPException(status_code=422, detail="Insufficient funds")

    system = get_or_create_system_account(db)

    txn = Transaction(
        transaction_type=TransactionType.withdrawal,
        source_account_id=data.account_id,
        destination_account_id=system.id,
        amount=data.amount,
        currency=data.currency,
        status=TransactionStatus.pending,
        description=data.description
    )
    db.add(txn)
    db.flush()

    db.add(LedgerEntry(account_id=data.account_id, transaction_id=txn.id, entry_type=EntryType.debit, amount=data.amount))

    txn.status = TransactionStatus.completed
    db.commit()
    db.refresh(txn)
    return txn