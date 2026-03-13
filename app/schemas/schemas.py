from pydantic import BaseModel, UUID4, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.models import AccountType, AccountStatus, TransactionType, TransactionStatus, EntryType
from decimal import Decimal


class AccountCreate(BaseModel):
    user_id: str
    account_type: AccountType
    currency: str = "USD"


class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    user_id: str
    account_type: AccountType
    currency: str
    status: AccountStatus
    created_at: datetime
    balance: Decimal


class LedgerEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    account_id: UUID4
    transaction_id: UUID4
    entry_type: EntryType
    amount: Decimal
    timestamp: datetime


class TransferRequest(BaseModel):
    source_account_id: UUID4
    destination_account_id: UUID4
    amount: Decimal
    currency: str = "USD"
    description: Optional[str] = None


class DepositRequest(BaseModel):
    account_id: UUID4
    amount: Decimal
    currency: str = "USD"
    description: Optional[str] = None


class WithdrawalRequest(BaseModel):
    account_id: UUID4
    amount: Decimal
    currency: str = "USD"
    description: Optional[str] = None


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    transaction_type: TransactionType
    source_account_id: Optional[UUID4]
    destination_account_id: Optional[UUID4]
    amount: Decimal
    currency: str
    status: TransactionStatus
    description: Optional[str]
    created_at: datetime