from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.schemas import TransferRequest, DepositRequest, WithdrawalRequest, TransactionResponse
from app.services.transaction_service import execute_transfer, execute_deposit, execute_withdrawal

router = APIRouter(tags=["Transactions"])


@router.post("/transfers", response_model=TransactionResponse, status_code=201)
def transfer(data: TransferRequest, db: Session = Depends(get_db)):
    return execute_transfer(db, data)


@router.post("/deposits", response_model=TransactionResponse, status_code=201)
def deposit(data: DepositRequest, db: Session = Depends(get_db)):
    return execute_deposit(db, data)


@router.post("/withdrawals", response_model=TransactionResponse, status_code=201)
def withdrawal(data: WithdrawalRequest, db: Session = Depends(get_db)):
    return execute_withdrawal(db, data)