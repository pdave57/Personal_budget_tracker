from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from app.database import get_db
from app.services.report_service import ReportService
from app.dependencies import get_current_active_user
from app.models.user import User


router = APIRouter(prefix="/reports", tags=["Reports"])


def get_report_service(db: Session = Depends(get_db)) -> ReportService:
    return ReportService(db)


@router.get("/summary")
def get_financial_summary(
    start_date: Optional[date] = Query(None, description="Start date (defaults to first day of current month)"),
    end_date: Optional[date] = Query(None, description="End date (defaults to last day of current month)"),
    service: ReportService = Depends(get_report_service),
    current_user: User = Depends(get_current_active_user),
):
    return service.get_financial_summary(current_user.id, start_date, end_date)


@router.get("/dashboard")
def get_dashboard_summary(
    start_date: Optional[date] = Query(None, description="Start date (defaults to first day of current month)"),
    end_date: Optional[date] = Query(None, description="End date (defaults to last day of current month)"),
    service: ReportService = Depends(get_report_service),
    current_user: User = Depends(get_current_active_user),
):
    return service.get_dashboard_summary(current_user.id, start_date, end_date)


@router.get("/income-by-category")
def get_income_by_category(
    start_date: Optional[date] = Query(None, description="Start date (defaults to first day of current month)"),
    end_date: Optional[date] = Query(None, description="End date (defaults to last day of current month)"),
    service: ReportService = Depends(get_report_service),
    current_user: User = Depends(get_current_active_user),
):
    return service.get_income_by_category(current_user.id, start_date, end_date)


@router.get("/expenses-by-category")
def get_expenses_by_category(
    start_date: Optional[date] = Query(None, description="Start date (defaults to first day of current month)"),
    end_date: Optional[date] = Query(None, description="End date (defaults to last day of current month)"),
    service: ReportService = Depends(get_report_service),
    current_user: User = Depends(get_current_active_user),
):
    return service.get_expenses_by_category(current_user.id, start_date, end_date)


@router.get("/monthly-summary/{year}")
@router.get("/monthly-summary")
def get_monthly_summary(
    year: Optional[int] = None,
    service: ReportService = Depends(get_report_service),
    current_user: User = Depends(get_current_active_user),
):
    return service.get_monthly_summary(current_user.id, year)


@router.get("/top-spending-categories")
def get_top_spending_categories(
    start_date: Optional[date] = Query(None, description="Start date (defaults to first day of current month)"),
    end_date: Optional[date] = Query(None, description="End date (defaults to last day of current month)"),
    limit: int = Query(5, ge=1, le=20),
    service: ReportService = Depends(get_report_service),
    current_user: User = Depends(get_current_active_user),
):
    return service.get_top_spending_categories(current_user.id, start_date, end_date, limit)
