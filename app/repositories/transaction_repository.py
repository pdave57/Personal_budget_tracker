from datetime import date
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionFilter


class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, transaction_id: int) -> Optional[Transaction]:
        return self.db.query(Transaction).filter(Transaction.id == transaction_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Transaction]:
        return self.db.query(Transaction).offset(skip).limit(limit).all()

    def get_filtered(
        self,
        filters: TransactionFilter,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Transaction]:
        query = self.db.query(Transaction)

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
        category_id: int,
        start_date: date,
        end_date: date,
    ) -> List[Transaction]:
        return (
            self.db.query(Transaction)
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
        type: str,
        start_date: date,
        end_date: date,
    ) -> Decimal:
        from sqlalchemy import func
        result = (
            self.db.query(func.sum(Transaction.amount))
            .filter(
                and_(
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
        category_id: int,
        start_date: date,
        end_date: date,
    ) -> Decimal:
        from sqlalchemy import func
        result = (
            self.db.query(func.sum(Transaction.amount))
            .filter(
                and_(
                    Transaction.category_id == category_id,
                    Transaction.transaction_date >= start_date,
                    Transaction.transaction_date <= end_date,
                )
            )
            .scalar()
        )
        return result or Decimal("0")

    def create(self, transaction: Transaction) -> Transaction:
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def update(self, transaction: Transaction) -> Transaction:
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def delete(self, transaction_id: int) -> bool:
        transaction = self.get_by_id(transaction_id)
        if transaction:
            self.db.delete(transaction)
            self.db.commit()
            return True
        return False