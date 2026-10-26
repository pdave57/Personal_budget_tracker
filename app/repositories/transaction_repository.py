from datetime import date
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionFilter


class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    def _base_query(self, user_id: int):
        return self.db.query(Transaction).filter(Transaction.user_id == user_id)

    def get_by_id(self, user_id: int, transaction_id: int) -> Optional[Transaction]:
        return self._base_query(user_id).filter(Transaction.id == transaction_id).first()

    def get_all(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Transaction]:
        return (
            self._base_query(user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_filtered(
        self,
        user_id: int,
        filters: TransactionFilter,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Transaction]:
        query = self._base_query(user_id)

        if filters.category_id:
            query = query.filter(Transaction.category_id == filters.category_id)
        if filters.type:
            query = query.filter(Transaction.type == filters.type)
        if filters.start_date:
            query = query.filter(Transaction.transaction_date >= filters.start_date)
        if filters.end_date:
            query = query.filter(Transaction.transaction_date <= filters.end_date)
        if filters.min_amount is not None:
            query = query.filter(Transaction.amount >= filters.min_amount)
        if filters.max_amount is not None:
            query = query.filter(Transaction.amount <= filters.max_amount)

        return query.order_by(Transaction.transaction_date.desc()).offset(skip).limit(limit).all()

    def get_by_category_and_date_range(
        self,
        user_id: int,
        category_id: int,
        start_date: date,
        end_date: date,
    ) -> List[Transaction]:
        return (
            self._base_query(user_id)
            .filter(
                and_(
                    Transaction.category_id == category_id,
                    Transaction.transaction_date >= start_date,
                    Transaction.transaction_date <= end_date,
                )
            )
            .all()
        )

    def get_total_by_type_and_date_range(
        self,
        user_id: int,
        type: str,
        start_date: date,
        end_date: date,
    ) -> Decimal:
        result = (
            self.db.query(func.sum(Transaction.amount))
            .filter(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.type == type,
                    Transaction.transaction_date >= start_date,
                    Transaction.transaction_date <= end_date,
                )
            )
            .scalar()
        )
        return result or Decimal("0")

    def get_total_by_category_and_date_range(
        self,
        user_id: int,
        category_id: int,
        start_date: date,
        end_date: date,
    ) -> Decimal:
        result = (
            self.db.query(func.sum(Transaction.amount))
            .filter(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.category_id == category_id,
                    Transaction.transaction_date >= start_date,
                    Transaction.transaction_date <= end_date,
                )
            )
            .scalar()
        )
        return result or Decimal("0")

    def create(self, transaction: Transaction, user_id: int) -> Transaction:
        transaction.user_id = user_id
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def update(self, transaction: Transaction) -> Transaction:
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def delete(self, user_id: int, transaction_id: int) -> bool:
        transaction = self.get_by_id(user_id, transaction_id)
        if transaction:
            self.db.delete(transaction)
            self.db.commit()
            return True
        return False
