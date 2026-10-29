from datetime import date
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.transaction import Transaction
from app.repositories.category_repository import CategoryRepository
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.transaction import TransactionCreate, TransactionFilter, TransactionUpdate


class TransactionService:
    def __init__(self, db: Session):
        self.transaction_repo = TransactionRepository(db)
        self.category_repo = CategoryRepository(db)

    def _validate_category(self, user_id: int, category_id: int, type: str) -> Category:
        category = self.category_repo.get_by_id(user_id, category_id)
        if not category:
            raise ValueError(f"Category with id {category_id} not found")
        if category.type != type:
            raise ValueError(f"Category {category.name} is not a {type} category")
        return category

    def create(self, user_id: int, data: TransactionCreate) -> Transaction:
        self._validate_category(user_id, data.category_id, data.type)
        transaction = Transaction(**data.model_dump())
        return self.transaction_repo.create(transaction, user_id)

    def get_by_id(self, user_id: int, transaction_id: int) -> Optional[Transaction]:
        return self.transaction_repo.get_by_id(user_id, transaction_id)

    def get_all(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Transaction]:
        return self.transaction_repo.get_all(user_id, skip, limit)

    def get_filtered(
        self,
        user_id: int,
        filters: TransactionFilter,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Transaction]:
        return self.transaction_repo.get_filtered(user_id, filters, skip, limit)

    def update(self, user_id: int, transaction_id: int, data: TransactionUpdate) -> Optional[Transaction]:
        transaction = self.get_by_id(user_id, transaction_id)
        if not transaction:
            return None

        update_data = data.model_dump(exclude_unset=True)
        if "category_id" in update_data or "type" in update_data:
            category_id = update_data.get("category_id", transaction.category_id)
            type = update_data.get("type", transaction.type)
            self._validate_category(user_id, category_id, type)

        for key, value in update_data.items():
            setattr(transaction, key, value)

        return self.transaction_repo.update(transaction)

    def delete(self, user_id: int, transaction_id: int) -> bool:
        return self.transaction_repo.delete(user_id, transaction_id)

    def get_total_income(self, user_id: int, start_date: date, end_date: date) -> Decimal:
        return self.transaction_repo.get_total_by_type_and_date_range(user_id, "income", start_date, end_date)

    def get_total_expenses(self, user_id: int, start_date: date, end_date: date) -> Decimal:
        return self.transaction_repo.get_total_by_type_and_date_range(user_id, "expense", start_date, end_date)

    def get_total_by_category(self, user_id: int, category_id: int, start_date: date, end_date: date) -> Decimal:
        return self.transaction_repo.get_total_by_category_and_date_range(user_id, category_id, start_date, end_date)

