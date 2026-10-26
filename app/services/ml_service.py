from datetime import date
from decimal import Decimal
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.repositories.transaction_repository import TransactionRepository
from app.repositories.category_repository import CategoryRepository
from app.models.transaction import Transaction
from app.models.category import Category
from app.models.budget import Budget


class MLBudgetService:
    """Machine Learning service for budget recommendations and overspending alerts."""

    def __init__(self):
        pass

    # ------------------------------------------------------------------ #
    # Overspending alert
    # ------------------------------------------------------------------ #
    def get_overspending_alerts(
        self,
        db: Session,
        month: int,
        year: int,
    ) -> List[dict]:
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)

        # Budgets for the month
        budgets = (
            db.query(Budget)
            .filter(Budget.month == month, Budget.year == year)
            .all()
        )

        # Expense spending per category for the month
        spending = (
            db.query(
                Transaction.category_id,
                func.sum(Transaction.amount).label("total"),
            )
            .filter(
                and_(
                    Transaction.type == "expense",
                    Transaction.transaction_date >= start_date,
                    Transaction.transaction_date < end_date,
                )
            )
            .group_by(Transaction.category_id)
            .all()
        )
        spent_by_cat: Dict[int, float] = {
            row.category_id: float(row.total) for row in spending
        }

        alerts: List[dict] = []
        total_budget = Decimal("0")
        total_spent = Decimal("0")
        over_count = 0

        for budget in budgets:
            category = budget.category
            if not category:
                continue
            spent = Decimal(str(spent_by_cat.get(budget.category_id, 0)))
            budget_amount = budget.amount
            remaining = budget_amount - spent
            pct = float((spent / budget_amount) * 100) if budget_amount > 0 else 0.0

            if spent > budget_amount:
                level = "critical"
            elif pct >= 80:
                level = "warning"
            else:
                level = "ok"

            if level != "ok":
                over_count += 1

            total_budget += budget_amount
            total_spent += spent

            alerts.append({
                "category_id": budget.category_id,
                "category_name": category.name,
                "budget_amount": float(budget_amount),
                "spent_amount": float(spent),
                "remaining": float(remaining),
                "percentage_used": round(pct, 2),
                "is_over": spent > budget_amount,
                "alert_level": level,
            })

        summary = {
            "total_budget": float(total_budget),
            "total_spent": float(total_spent),
            "total_remaining": float(total_budget - total_spent),
            "over_budget_count": over_count,
            "within_budget": total_spent <= total_budget,
        }

        alerts.sort(key=lambda a: a["percentage_used"], reverse=True)
        return {"alerts": alerts, "summary": summary}

    # ------------------------------------------------------------------ #
    # Recommender
    # ------------------------------------------------------------------ #
    def get_recommendations(self, db: Session) -> List[dict]:
        """Recommend budget adjustments per category using historical spending.

        Clusters expense categories by their average monthly spend (KMeans) and
        recommends a budget based on the category's cluster tier and history.
        """
        transactions = TransactionRepository(db).get_all()
        expense_tx = [t for t in transactions if t.type == "expense"]

        # Average monthly spend per category over available history
        monthly_totals: Dict[int, Dict[Tuple[int, int], float]] = defaultdict(
            lambda: defaultdict(float)
        )
        for t in expense_tx:
            key = (t.transaction_date.year, t.transaction_date.month)
            monthly_totals[t.category_id][key] += float(t.amount)

        category_repo = CategoryRepository(db)
        category_names = {
            c.id: c.name for c in category_repo.get_all()
        }

        records: List[dict] = []
        for category_id, months in monthly_totals.items():
            if not months:
                continue
            avg_monthly = sum(months.values()) / len(months)
            records.append({
                "category_id": category_id,
                "category_name": category_names.get(category_id, f"Category {category_id}"),
                "historical_avg": round(avg_monthly, 2),
                "months_tracked": len(months),
            })

        if not records:
            return []

        # Cluster categories by average monthly spend into low/medium/high tiers
        X = np.array([[r["historical_avg"]] for r in records], dtype=float)
        n_clusters = min(3, len(records))
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_scaled)

        # Map cluster -> tier by mean spend
        cluster_means: Dict[int, float] = defaultdict(list)
        for rec, label in zip(records, labels):
            cluster_means[label].append(rec["historical_avg"])
        tier_order = sorted(
            cluster_means.items(),
            key=lambda item: np.mean(item[1]),
        )
        tier_map = {
            label: tier_name
            for tier_name, (label, _) in zip(
                ["low", "medium", "high"], tier_order
            )
        }

        recommendations: List[dict] = []
        for rec, label in zip(records, labels):
            tier = tier_map[label]
            hist_avg = rec["historical_avg"]

            if tier == "high":
                action = "decrease"
                recommended = round(hist_avg * 0.9, 2)
                reason = "High-spend category; consider reducing budget by ~10%"
            elif tier == "low":
                action = "maintain"
                recommended = round(hist_avg * 1.05, 2)
                reason = "Low-spend category; keep current budget with small buffer"
            else:
                action = "maintain"
                recommended = round(hist_avg * 1.0, 2)
                reason = "Moderate spend; align budget with historical average"

            recommendations.append({
                "category_id": rec["category_id"],
                "category_name": rec["category_name"],
                "historical_avg": rec["historical_avg"],
                "recommended_budget": recommended,
                "current_budget": None,
                "action": action,
                "reason": reason,
            })

        recommendations.sort(key=lambda r: r["historical_avg"], reverse=True)
        return recommendations


ml_service = MLBudgetService()
