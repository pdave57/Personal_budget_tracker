from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, condecimal


Amount = condecimal(max_digits=12, decimal_places=2, gt=0)
OptionalAmount = condecimal(max_digits=12, decimal_places=2, gt=0)


class TransactionBase(BaseModel):
    category_id: int
    type: str  # "income" or "expense"
    amount: Amount
    description: Optional[str] = None
    transaction_date: date


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    category_id: Optional[int] = None
    type: Optional[str] = None
    amount: Optional[Amount] = None
    description: Optional[str] = None
    transaction_date: Optional[date] = None


class TransactionResponse(TransactionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class TransactionFilter(BaseModel):
    category_id: Optional[int] = None
    type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None