from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field

from app.schemas.category import CategoryResponse


class BudgetBase(BaseModel):
    category_id: int
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2000)


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BaseModel):
    amount: Optional[Decimal] = Field(default=None, gt=0, decimal_places=2)


class BudgetResponse(BudgetBase):
    id: int
    category: Optional[CategoryResponse] = None

    class Config:
        from_attributes = True
