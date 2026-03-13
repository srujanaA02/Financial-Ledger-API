import uuid
from datetime import datetime,timezone
from sqlalchemy import Column, String, Numeric, DateTime, Enum, ForeignKey, event, TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


# ─────────────────────────────────────────────
# Platform-independent UUID (PostgreSQL + SQLite)
# ─────────────────────────────────────────────
class UUID(TypeDecorator):
    """Works with PostgreSQL (native UUID) and SQLite (CHAR 36) for tests."""
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return str(value)
        if not isinstance(value, uuid.UUID):
            return str(uuid.UUID(str(value)))
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if not isinstance(value, uuid.UUID):
            return uuid.UUID(str(value))
        return value


# ─────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────
class AccountType(str, enum.Enum):
    checking = "checking"
    savings = "savings"


class AccountStatus(str, enum.Enum):
    active = "active"
    frozen = "frozen"


class TransactionType(str, enum.Enum):
    transfer = "transfer"
    deposit = "deposit"
    withdrawal = "withdrawal"


class TransactionStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


class EntryType(str, enum.Enum):
    debit = "debit"
    credit = "credit"


# ─────────────────────────────────────────────
# Models
# ─────────────────────────────────────────────
class Account(Base):
    __tablename__ = "accounts"

    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False)
    account_type = Column(Enum(AccountType), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    status = Column(Enum(AccountStatus), nullable=False, default=AccountStatus.active)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    ledger_entries = relationship("LedgerEntry", back_populates="account")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    source_account_id = Column(UUID(), ForeignKey("accounts.id"), nullable=True)
    destination_account_id = Column(UUID(), ForeignKey("accounts.id"), nullable=True)
    amount = Column(Numeric(precision=20, scale=4), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    status = Column(Enum(TransactionStatus), nullable=False, default=TransactionStatus.pending)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    ledger_entries = relationship("LedgerEntry", back_populates="transaction")


class LedgerEntry(Base):
    __tablename__ = "ledger_entries"

    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(), ForeignKey("accounts.id"), nullable=False)
    transaction_id = Column(UUID(), ForeignKey("transactions.id"), nullable=False)
    entry_type = Column(Enum(EntryType), nullable=False)
    amount = Column(Numeric(precision=20, scale=4), nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    account = relationship("Account", back_populates="ledger_entries")
    transaction = relationship("Transaction", back_populates="ledger_entries")


# ─────────────────────────────────────────────
# Immutability Guards
# ─────────────────────────────────────────────
@event.listens_for(LedgerEntry, "before_update")
def block_ledger_update(mapper, connection, target):
    raise Exception("Ledger entries are immutable and cannot be updated.")


@event.listens_for(LedgerEntry, "before_delete")
def block_ledger_delete(mapper, connection, target):
    raise Exception("Ledger entries are immutable and cannot be deleted.")