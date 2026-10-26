# Personal Budget Tracker API

A FastAPI-based REST API for tracking personal income, expenses, budgets, and financial reports.

## Features

- **Authentication**: JWT-based authentication (Register / Login)
- **Categories**: Organize income and expense categories
- **Transactions**: Record and filter income/expense transactions
- **Budgets**: Set and monitor category budgets per month/year
- **Reports**: Financial summaries, category breakdowns, and monthly trends

## Tech Stack

- **Framework**: FastAPI
- **Database**: SQLite (SQLAlchemy ORM)
- **Validation**: Pydantic
- **Security**: Passlib (sha256_crypt) & Python-Jose (JWT)

## Getting Started

### 1. Set Up Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Environment Variables

Create `.env` file or configure:
```env
DATABASE_URL=sqlite:///./budget_tracker.db
DEBUG=True
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Run the Application

```bash
uvicorn app.main:app --reload
```

Interactive API documentation will be available at:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
