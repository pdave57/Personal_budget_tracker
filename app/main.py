from fastapi import FastAPI
from app.config import get_settings
from app.database import init_db
from app.routers import (
    categories_router,
    transactions_router,
    budgets_router,
    reports_router,
    auth_router,
)

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


app.include_router(auth_router)
app.include_router(categories_router)
app.include_router(transactions_router)
app.include_router(budgets_router)
app.include_router(reports_router)


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