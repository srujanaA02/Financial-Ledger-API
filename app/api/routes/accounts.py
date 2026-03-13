from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.schemas import AccountCreate, AccountResponse, LedgerEntryResponse
from app.services.account_service import create_account, get_account, calculate_balance, get_ledger_entries
from app.models.models import EntryType
from typing import List, Optional
import uuid

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post("", response_model=AccountResponse, status_code=201,
    summary="Create a new account",
    description="Creates a new bank account for a user with checking or savings type.")
def create_new_account(data: AccountCreate, db: Session = Depends(get_db)):
    account = create_account(db, data)
    balance = calculate_balance(db, account.id)
    return AccountResponse(
        id=account.id, user_id=account.user_id, account_type=account.account_type,
        currency=account.currency, status=account.status,
        created_at=account.created_at, balance=balance
    )


@router.get("/{account_id}", response_model=AccountResponse,
    summary="Get account details",
    description="Retrieve account details including the real-time calculated balance.")
def get_account_details(account_id: uuid.UUID, db: Session = Depends(get_db)):
    account = get_account(db, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    balance = calculate_balance(db, account_id)
    return AccountResponse(
        id=account.id, user_id=account.user_id, account_type=account.account_type,
        currency=account.currency, status=account.status,
        created_at=account.created_at, balance=balance
    )


@router.get("/{account_id}/ledger", response_model=dict,
    summary="Get account ledger",
    description="Fetch paginated ledger entries for an account, with optional filtering by entry type.")
def get_account_ledger(
    account_id: uuid.UUID,
    db: Session = Depends(get_db),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items per page"),
    entry_type: Optional[EntryType] = Query(default=None, description="Filter by debit or credit")
):
    account = get_account(db, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    entries = get_ledger_entries(db, account_id, entry_type=entry_type)
    total = len(entries)
    start = (page - 1) * page_size
    end = start + page_size
    paginated = entries[start:end]

    return {
        "account_id": str(account_id),
        "page": page,
        "page_size": page_size,
        "total_entries": total,
        "total_pages": (total + page_size - 1) // page_size,
        "entries": [LedgerEntryResponse.model_validate(e) for e in paginated]
    }