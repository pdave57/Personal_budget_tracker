from app.routers.categories import router as categories_router
from app.routers.transactions import router as transactions_router
from app.routers.budgets import router as budgets_router
from app.routers.reports import router as reports_router
from app.routers.auth import router as auth_router
from app.routers.ml import router as ml_router

__all__ = [
    "categories_router",
    "transactions_router",
    "budgets_router",
    "reports_router",
    "auth_router",
    "ml_router",
]