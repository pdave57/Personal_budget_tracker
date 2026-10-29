from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.ml_service import ml_service
from app.schemas.ml import (
    OverspendingAlert,
    BudgetRecommendation,
    RecommendationResponse,
    AlertResponse,
)
from app.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/ml", tags=["Machine Learning"])


@router.get("/recommend", response_model=RecommendationResponse)
def get_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    recommendations = ml_service.get_recommendations(db, current_user.id)
    return RecommendationResponse(
        recommendations=[BudgetRecommendation(**r) for r in recommendations],
        generated_at=date.today().isoformat(),
    )


@router.get("/alerts", response_model=AlertResponse)
def get_overspending_alerts(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = ml_service.get_overspending_alerts(db, current_user.id, month, year)
    return AlertResponse(
        alerts=[OverspendingAlert(**a) for a in result["alerts"]],
        summary=result["summary"],
        month=month,
        year=year,
    )
