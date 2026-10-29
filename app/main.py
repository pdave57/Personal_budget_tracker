from datetime import date
from typing import Optional
from fastapi import FastAPI, Depends, Query

from app.config import get_settings
from app.database import init_db
from app.dependencies import get_current_active_user
from app.models.user import User
from app.routers import (
    categories_router,
    transactions_router,
    budgets_router,
    reports_router,
    auth_router,
    ml_router,
)
from app.routers.reports import get_report_service
from app.services.report_service import ReportService

settings = get_settings()

app = FastAPI(
    title="Personal Budget Tracker API",
    description="API for tracking personal income, expenses, and budgets",
    version="1.0.0",
    debug=settings.debug,
)


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(auth_router, prefix="/api/v1")
app.include_router(categories_router, prefix="/api/v1")
app.include_router(transactions_router, prefix="/api/v1")
app.include_router(budgets_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")
app.include_router(ml_router, prefix="/api/v1")


@app.get("/api/v1/dashboard", tags=["Dashboard"])
def get_dashboard(
    start_date: Optional[date] = Query(None, description="Start date (defaults to first day of current month)"),
    end_date: Optional[date] = Query(None, description="End date (defaults to last day of current month)"),
    service: ReportService = Depends(get_report_service),
    current_user: User = Depends(get_current_active_user),
):
    return service.get_dashboard_summary(current_user.id, start_date, end_date)


@app.get("/")
def root():

    return {
        "message": "Personal Budget Tracker API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}