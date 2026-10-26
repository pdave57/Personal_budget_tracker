from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class OverspendingAlert(BaseModel):
    category_id: int
    category_name: str
    budget_amount: float
    spent_amount: float
    remaining: float
    percentage_used: float
    is_over: bool
    alert_level: str = Field(..., description="critical | warning | ok")


class BudgetRecommendation(BaseModel):
    category_id: int
    category_name: str
    historical_avg: float
    recommended_budget: float
    current_budget: Optional[float]
    action: str = Field(..., description="increase | decrease | maintain")
    reason: str


class RecommendationResponse(BaseModel):
    recommendations: List[BudgetRecommendation]
    generated_at: str


class AlertResponse(BaseModel):
    alerts: List[OverspendingAlert]
    summary: Dict[str, Any]
    month: int
    year: int
