from typing import Optional
from pydantic import BaseModel


class CategoryBase(BaseModel):
    name: str
    type: str  # "income" or "expense"


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None


class CategoryResponse(CategoryBase):
    id: int

    class Config:
        from_attributes = True

