from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, condecimal

from app.schemas.category import CategoryResponse


BudgetAmount = condecimal(max_digits=12, decimal_places=2, gt=0)
OptionalBudgetAmount = condecimal(max_digits=12, decimal_places=2, gt=0)


class BudgetBase(BaseModel):
    category_id: int
    amount: BudgetAmount
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2000)


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BaseModel):
    amount: Optional[BudgetAmount] = None


class BudgetResponse(BudgetBase):
    id: int
    category: Optional[CategoryResponse] = None

    class Config:
        from_attributes = True

