from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from app.database import get_db
from app.services.budget_service import BudgetService
from app.schemas.budget import BudgetCreate, BudgetResponse, BudgetUpdate
from app.dependencies import get_current_active_user
from app.models.user import User


router = APIRouter(prefix="/budgets", tags=["Budgets"])


def get_budget_service(db: Session = Depends(get_db)) -> BudgetService:
    return BudgetService(db)


@router.post("", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def create_budget(
    data: BudgetCreate,
    service: BudgetService = Depends(get_budget_service),
    current_user: User = Depends(get_current_active_user),
):
    try:
        return service.create(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[BudgetResponse])
def list_budgets(
    skip: int = 0,
    limit: int = 100,
    service: BudgetService = Depends(get_budget_service),
    current_user: User = Depends(get_current_active_user),
):
    return service.get_all(skip, limit)


@router.get("/month/{month}/year/{year}", response_model=List[BudgetResponse])
def get_budgets_by_month_year(
    month: int,
    year: int,
    service: BudgetService = Depends(get_budget_service),
    current_user: User = Depends(get_current_active_user),
):
    return service.get_by_month_year(month, year)


@router.get("/category/{category_id}", response_model=List[BudgetResponse])
def get_budgets_by_category(
    category_id: int,
    service: BudgetService = Depends(get_budget_service),
    current_user: User = Depends(get_current_active_user),
):
    return service.get_by_category(category_id)


@router.get("/{budget_id}", response_model=BudgetResponse)
def get_budget(
    budget_id: int,
    service: BudgetService = Depends(get_budget_service),
    current_user: User = Depends(get_current_active_user),
):
    budget = service.get_by_id(budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return budget


@router.get("/status/category/{category_id}/month/{month}/year/{year}")
def get_budget_status(
    category_id: int,
    month: int,
    year: int,
    service: BudgetService = Depends(get_budget_service),
    current_user: User = Depends(get_current_active_user),
):
    return service.get_budget_status(category_id, month, year)


@router.get("/status/month/{month}/year/{year}")
def get_all_budget_statuses(
    month: int,
    year: int,
    service: BudgetService = Depends(get_budget_service),
    current_user: User = Depends(get_current_active_user),
):
    return service.get_all_budget_statuses(month, year)


@router.put("/{budget_id}", response_model=BudgetResponse)
def update_budget(
    budget_id: int,
    data: BudgetUpdate,
    service: BudgetService = Depends(get_budget_service),
    current_user: User = Depends(get_current_active_user),
):
    try:
        budget = service.update(budget_id, data)
        if not budget:
            raise HTTPException(status_code=404, detail="Budget not found")
        return budget
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    budget_id: int,
    service: BudgetService = Depends(get_budget_service),
    current_user: User = Depends(get_current_active_user),
):
    if not service.delete(budget_id):
        raise HTTPException(status_code=404, detail="Budget not found")