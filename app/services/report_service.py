from datetime import date
from decimal import Decimal
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models.category import Category
from app.models.transaction import Transaction
from app.repositories.category_repository import CategoryRepository


class ReportService:
    def __init__(self, db: Session):
        self.db = db
        self.category_repo = CategoryRepository(db)

    def get_financial_summary(self, start_date: date, end_date: date) -> Dict[str, Any]:
        total_income = (
            self.db.query(func.sum(Transaction.amount))
            .filter(
                and_(
                    Transaction.type == "income",
                    Transaction.transaction_date >= start_date,
                    Transaction.transaction_date <= end_date,
                )
            )
            .scalar()
            or Decimal("0")
        )

        total_expenses = (
            self.db.query(func.sum(Transaction.amount))
            .filter(
                and_(
                    Transaction.type == "expense",
                    Transaction.transaction_date >= start_date,
                    Transaction.transaction_date <= end_date,
                )
            )
            .scalar()
            or Decimal("0")
        )

        net_cash_flow = total_income - total_expenses

        return {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_cash_flow": net_cash_flow,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        }

    def get_income_by_category(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        results = (
            self.db.query(
                Category.name,
                func.sum(Transaction.amount).label("total"),
            )
            .join(Transaction, Transaction.category_id == Category.id)
            .filter(
                and_(
                    Transaction.type == "income",
                    Transaction.transaction_date >= start_date,
                    Transaction.transaction_date <= end_date,
                )
            )
            .group_by(Category.id, Category.name)
            .all()
        )

        total_income = sum(amount for _, amount in results) if results else Decimal("0")

        return [
            {
                "category": name,
                "amount": amount,
                "percentage": float((amount / total_income) * 100) if total_income > 0 else 0,
            }
            for name, amount in results
        ]

    def get_expenses_by_category(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        results = (
            self.db.query(
                Category.name,
                func.sum(Transaction.amount).label("total"),
            )
            .join(Transaction, Transaction.category_id == Category.id)
            .filter(
                and_(
                    Transaction.type == "expense",
                    Transaction.transaction_date >= start_date,
                    Transaction.transaction_date <= end_date,
                )
            )
            .group_by(Category.id, Category.name)
            .all()
        )

        total_expenses = sum(amount for _, amount in results) if results else Decimal("0")

        return [
            {
                "category": name,
                "amount": amount,
                "percentage": float((amount / total_expenses) * 100) if total_expenses > 0 else 0,
            }
            for name, amount in results
        ]

    def get_monthly_summary(self, year: int) -> List[Dict[str, Any]]:
        results = (
            self.db.query(
                func.extract("month", Transaction.transaction_date).label("month"),
                Transaction.type,
                func.sum(Transaction.amount).label("total"),
            )
            .filter(func.extract("year", Transaction.transaction_date) == year)
            .group_by(
                func.extract("month", Transaction.transaction_date),
                Transaction.type,
            )
            .all()
        )

        monthly_data = {}
        for month, type, total in results:
            month = int(month)
            if month not in monthly_data:
                monthly_data[month] = {
                    "month": month,
                    "income": Decimal("0"),
                    "expenses": Decimal("0"),
                }
            if type == "income":
                monthly_data[month]["income"] = total
            else:
                monthly_data[month]["expenses"] = total

        summary = []
        for month in range(1, 13):
            data = monthly_data.get(
                month,
                {"month": month, "income": Decimal("0"), "expenses": Decimal("0")},
            )
            data["net"] = data["income"] - data["expenses"]
            summary.append(data)

        return summary

    def get_top_spending_categories(
        self,
        start_date: date,
        end_date: date,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        results = (
            self.db.query(
                Category.name,
                func.sum(Transaction.amount).label("total"),
            )
            .join(Transaction, Transaction.category_id == Category.id)
            .filter(
                and_(
                    Transaction.type == "expense",
                    Transaction.transaction_date >= start_date,
                    Transaction.transaction_date <= end_date,
                )
            )
            .group_by(Category.id, Category.name)
            .order_by(func.sum(Transaction.amount).desc())
            .limit(limit)
            .all()
        )

        return [
            {"category": name, "amount": amount}
            for name, amount in results
        ]

