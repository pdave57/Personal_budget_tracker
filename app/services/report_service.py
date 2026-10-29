import calendar
from datetime import date
from decimal import Decimal
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models.category import Category
from app.models.transaction import Transaction
from app.repositories.category_repository import CategoryRepository


class ReportService:
    def __init__(self, db: Session):
        self.db = db
        self.category_repo = CategoryRepository(db)

    @staticmethod
    def _resolve_date_range(start_date: Optional[date] = None, end_date: Optional[date] = None) -> Tuple[date, date]:
        today = date.today()
        if start_date is None:
            start_date = today.replace(day=1)
        if end_date is None:
            _, last_day = calendar.monthrange(today.year, today.month)
            end_date = today.replace(day=last_day)
        return start_date, end_date

    def get_financial_summary(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        start_date, end_date = self._resolve_date_range(start_date, end_date)

        total_income = (
            self.db.query(func.sum(Transaction.amount))
            .filter(
                and_(
                    Transaction.user_id == user_id,
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
                    Transaction.user_id == user_id,
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
            "income": total_income,
            "expenses": total_expenses,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        }

    def get_income_by_category(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        start_date, end_date = self._resolve_date_range(start_date, end_date)

        results = (
            self.db.query(
                Category.name,
                func.sum(Transaction.amount).label("total"),
            )
            .join(Transaction, Transaction.category_id == Category.id)
            .filter(
                and_(
                    Transaction.user_id == user_id,
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

    def get_expenses_by_category(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        start_date, end_date = self._resolve_date_range(start_date, end_date)

        results = (
            self.db.query(
                Category.name,
                func.sum(Transaction.amount).label("total"),
            )
            .join(Transaction, Transaction.category_id == Category.id)
            .filter(
                and_(
                    Transaction.user_id == user_id,
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

    def get_monthly_summary(self, user_id: int, year: Optional[int] = None) -> List[Dict[str, Any]]:
        if year is None:
            year = date.today().year

        results = (
            self.db.query(
                func.extract("month", Transaction.transaction_date).label("month"),
                Transaction.type,
                func.sum(Transaction.amount).label("total"),
            )
            .filter(
                and_(
                    Transaction.user_id == user_id,
                    func.extract("year", Transaction.transaction_date) == year,
                )
            )
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
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        start_date, end_date = self._resolve_date_range(start_date, end_date)

        results = (
            self.db.query(
                Category.name,
                func.sum(Transaction.amount).label("total"),
            )
            .join(Transaction, Transaction.category_id == Category.id)
            .filter(
                and_(
                    Transaction.user_id == user_id,
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

    def get_dashboard_summary(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        start_date, end_date = self._resolve_date_range(start_date, end_date)
        financial_summary = self.get_financial_summary(user_id, start_date, end_date)
        income_by_cat = self.get_income_by_category(user_id, start_date, end_date)
        expenses_by_cat = self.get_expenses_by_category(user_id, start_date, end_date)
        top_spending = self.get_top_spending_categories(user_id, start_date, end_date, limit=5)

        return {
            **financial_summary,
            "income_by_category": income_by_cat,
            "expenses_by_category": expenses_by_cat,
            "top_spending_categories": top_spending,
        }


