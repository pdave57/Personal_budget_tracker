from datetime import date
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.budget import Budget
from app.models.category import Category
from app.models.transaction import Transaction
from app.repositories.category_repository import CategoryRepository
from app.schemas.budget import BudgetCreate, BudgetUpdate


class BudgetService:
    def __init__(self, db: Session):
        self.db = db
        self.category_repo = CategoryRepository(db)
        self.user_id: Optional[int] = None

    def _validate_category(self, category_id: int) -> Category:
        if self.user_id is None:
            raise ValueError("User context is required")
        category = self.category_repo.get_by_id(self.user_id, category_id)
        if not category:
            raise ValueError(f"Category with id {category_id} not found")
        if category.type != "expense":
            raise ValueError(f"Category {category.name} is not an expense category")
        return category

    def create(self, data: BudgetCreate) -> Budget:
        self._validate_category(data.category_id)

        existing = (
            self.db.query(Budget)
            .filter(
                and_(
                    Budget.user_id == self.user_id,
                    Budget.category_id == data.category_id,
                    Budget.month == data.month,
                    Budget.year == data.year,
                )
            )
            .first()
        )
        if existing:
            raise ValueError("Budget for this category and month/year already exists")

        budget = Budget(**data.model_dump())
        budget.user_id = self.user_id
        self.db.add(budget)
        self.db.commit()
        self.db.refresh(budget)
        return budget

    def get_by_id(self, budget_id: int) -> Optional[Budget]:
        if self.user_id is None:
            return None
        return self.db.query(Budget).filter(Budget.user_id == self.user_id, Budget.id == budget_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Budget]:
        if self.user_id is None:
            return []
        return self.db.query(Budget).filter(Budget.user_id == self.user_id).offset(skip).limit(limit).all()

    def get_by_category(self, category_id: int) -> List[Budget]:
        if self.user_id is None:
            return []
        return self.db.query(Budget).filter(Budget.user_id == self.user_id, Budget.category_id == category_id).all()

    def get_by_month_year(self, month: int, year: int) -> List[Budget]:
        if self.user_id is None:
            return []
        return (
            self.db.query(Budget)
            .filter(and_(Budget.user_id == self.user_id, Budget.month == month, Budget.year == year))
            .all()
        )

    def update(self, budget_id: int, data: BudgetUpdate) -> Optional[Budget]:
        budget = self.get_by_id(budget_id)
        if not budget:
            return None

        update_data = data.model_dump(exclude_unset=True)

        if "category_id" in update_data:
            self._validate_category(update_data["category_id"])

        for key, value in update_data.items():
            setattr(budget, key, value)

        self.db.commit()
        self.db.refresh(budget)
        return budget

    def delete(self, budget_id: int) -> bool:
        budget = self.get_by_id(budget_id)
        if budget:
            self.db.delete(budget)
            self.db.commit()
            return True
        return False

    def get_budget_status(
        self,
        category_id: int,
        month: int,
        year: int,
    ) -> dict:
        if self.user_id is None:
            return {
                "budget_id": None,
                "category_id": category_id,
                "budget_amount": None,
                "spent_amount": Decimal("0"),
                "remaining": Decimal("0"),
                "percentage_used": 0,
                "exceeded": False,
            }

        budget = (
            self.db.query(Budget)
            .filter(
                and_(
                    Budget.user_id == self.user_id,
                    Budget.category_id == category_id,
                    Budget.month == month,
                    Budget.year == year,
                )
            )
            .first()
        )

        if not budget:
            return {
                "budget_id": None,
                "category_id": category_id,
                "budget_amount": None,
                "spent_amount": Decimal("0"),
                "remaining": Decimal("0"),
                "percentage_used": 0,
                "exceeded": False,
            }

        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)
        end_date = date(end_date.year, end_date.month, end_date.day)

        spent = (
            self.db.query(Transaction)
            .filter(
                and_(
                    Transaction.user_id == self.user_id,
                    Transaction.category_id == category_id,
                    Transaction.transaction_date >= start_date,
                    Transaction.transaction_date < end_date,
                    Transaction.type == "expense",
                )
            )
            .with_entities(Transaction.amount)
            .all()
        )
        spent_amount = sum(s[0] for s in spent) if spent else Decimal("0")

        remaining = budget.amount - spent_amount
        percentage_used = float(spent_amount / budget.amount * 100) if budget.amount > 0 else 0

        return {
            "budget_id": budget.id,
            "category_id": category_id,
            "budget_amount": budget.amount,
            "spent_amount": spent_amount,
            "remaining": remaining,
            "percentage_used": round(percentage_used, 2),
            "exceeded": spent_amount > budget.amount,
        }

    def get_all_budget_statuses(self, month: int, year: int) -> List[dict]:
        budgets = self.get_by_month_year(month, year)
        return [self.get_budget_status(b.category_id, month, year) for b in budgets]