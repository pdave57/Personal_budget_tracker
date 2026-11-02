import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import date
from typing import Optional

import httpx
from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware

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

logger = logging.getLogger(__name__)

settings = get_settings()


async def _keep_alive_loop(url: str, interval: int) -> None:
    """Periodically ping the given URL to prevent Render free-tier cold starts."""
    logger.info("Keep-alive task started — pinging %s every %d seconds", url, interval)
    async with httpx.AsyncClient(timeout=30) as client:
        while True:
            await asyncio.sleep(interval)
            try:
                response = await client.get(url)
                logger.info(
                    "Keep-alive ping to %s — status %d", url, response.status_code
                )
            except Exception as exc:
                logger.warning("Keep-alive ping to %s failed: %s", url, exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──
    init_db()

    keep_alive_task = None
    if settings.keep_alive_url:
        keep_alive_task = asyncio.create_task(
            _keep_alive_loop(settings.keep_alive_url, settings.keep_alive_interval)
        )

    yield

    # ── Shutdown ──
    if keep_alive_task is not None:
        keep_alive_task.cancel()
        try:
            await keep_alive_task
        except asyncio.CancelledError:
            logger.info("Keep-alive task cancelled")


app = FastAPI(
    title="Personal Budget Tracker API",
    description="API for tracking personal income, expenses, and budgets",
    version="1.0.0",
    debug=settings.debug,
    lifespan=lifespan,
)

# CORS configuration — allow the frontend origin(s)
allowed_origins = [
    origin.strip()
    for origin in settings.cors_origins.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
