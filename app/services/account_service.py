from sqlalchemy.orm import Session
from app.models.models import Account, LedgerEntry, EntryType
from app.schemas.schemas import AccountCreate
from decimal import Decimal
from typing import Optional
import uuid


def create_account(db: Session, data: AccountCreate) -> Account:
    account = Account(
        user_id=data.user_id,
        account_type=data.account_type,
        currency=data.currency
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


def get_account(db: Session, account_id: uuid.UUID):
    return db.query(Account).filter(Account.id == account_id).first()


def calculate_balance(db: Session, account_id: uuid.UUID) -> Decimal:
    entries = db.query(LedgerEntry).filter(LedgerEntry.account_id == account_id).all()
    balance = Decimal("0")
    for entry in entries:
        if entry.entry_type == EntryType.credit:
            balance += entry.amount
        else:
            balance -= entry.amount
    return balance


def get_ledger_entries(db: Session, account_id: uuid.UUID, entry_type: Optional[EntryType] = None):
    query = db.query(LedgerEntry).filter(LedgerEntry.account_id == account_id)
    if entry_type:
        query = query.filter(LedgerEntry.entry_type == entry_type)
    return query.order_by(LedgerEntry.timestamp.asc()).all()