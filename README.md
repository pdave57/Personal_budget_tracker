# Personal Budget Tracker API

A FastAPI-based REST API for tracking personal income, expenses, budgets, and financial reports — with ML-powered budget recommendations and overspending alerts.

## Features

- **Authentication**: JWT-based authentication (Register / Login)
- **Categories**: Organize income and expense categories
- **Transactions**: Record and filter income/expense transactions
- **Budgets**: Set and monitor category budgets per month/year
- **Reports**: Financial summaries, category breakdowns, and monthly trends
- **ML Insights**: Budget recommendations and overspending alerts powered by scikit-learn

## Tech Stack

- **Framework**: FastAPI
- **Database**: SQLite (SQLAlchemy ORM)
- **Validation**: Pydantic
- **Security**: Passlib (sha256_crypt) & Python-Jose (JWT)
- **ML**: scikit-learn, NumPy

---

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                        CLIENT                                │
│              (Browser / Postman / Frontend)                   │
└──────────────────────┬───────────────────────────────────────┘
                       │  HTTP Requests
                       ▼
┌──────────────────────────────────────────────────────────────┐
│                    FastAPI Application                        │
│                      (app/main.py)                            │
│                                                              │
│  ┌──────────┐  ┌─────────────┐  ┌──────────┐  ┌───────────┐ │
│  │  /auth   │  │/categories  │  │/budgets  │  │ /reports  │ │
│  │  Router  │  │   Router    │  │  Router  │  │  Router   │ │
│  └────┬─────┘  └──────┬──────┘  └────┬─────┘  └─────┬─────┘ │
│       │               │              │               │       │
│  ┌────┴───┐    ┌──────┴──────┐  ┌────┴─────┐  ┌─────┴─────┐ │
│  │/trans- │    │    /ml      │  │          │  │           │ │
│  │actions │    │   Router    │  │          │  │           │ │
│  │Router  │    └──────┬──────┘  │          │  │           │ │
│  └───┬────┘           │         │          │  │           │ │
│      │                │         │          │  │           │ │
│  ────┴────────────────┴─────────┴──────────┴──┴───────────┘ │
│                 ROUTER LAYER (app/routers/)                   │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────────┐│
│  │              DEPENDENCY INJECTION LAYER                  ││
│  │         (app/dependencies.py — JWT Auth Guard)           ││
│  └──────────────────────────────────────────────────────────┘│
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────────┐│
│  │  Transaction  │  │    Budget     │  │     Report        ││
│  │   Service     │  │   Service     │  │    Service        ││
│  └───────┬───────┘  └───────┬───────┘  └────────┬──────────┘│
│          │                  │                    │           │
│  ┌───────┴───────┐  ┌──────┴──────┐   ┌────────┴─────────┐ │
│  │  Auth Service │  │  ML Budget  │   │                   │ │
│  │               │  │   Service   │   │                   │ │
│  └───────────────┘  └─────────────┘   │                   │ │
│                 SERVICE LAYER (app/services/)               │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────┐  ┌─────────────────────────────┐│
│  │  CategoryRepository    │  │ TransactionRepository       ││
│  └───────────┬────────────┘  └──────────────┬──────────────┘│
│              │   REPOSITORY LAYER            │              │
│              │   (app/repositories/)         │              │
├──────────────┴───────────────────────────────┴──────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────────┐│
│  │                  SQLAlchemy ORM                          ││
│  │              MODEL LAYER (app/models/)                   ││
│  │  ┌──────────┐ ┌─────────────┐ ┌────────┐ ┌──────┐      ││
│  │  │ Category │ │ Transaction │ │ Budget │ │ User │      ││
│  │  └──────────┘ └─────────────┘ └────────┘ └──────┘      ││
│  └──────────────────────────────────────────────────────────┘│
│                                                              │
├──────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────┐│
│  │               SQLite Database                            ││
│  │             (budget_tracker.db)                           ││
│  └──────────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────┘
```

### Layered Architecture Summary

| Layer          | Directory             | Responsibility                                             |
|----------------|-----------------------|------------------------------------------------------------|
| **Routers**    | `app/routers/`        | HTTP endpoints, request parsing, response formatting       |
| **Schemas**    | `app/schemas/`        | Pydantic models for request/response validation            |
| **Dependencies** | `app/dependencies.py` | JWT authentication guard & shared dependencies           |
| **Services**   | `app/services/`       | Business logic, validation rules, ML recommendations       |
| **Repositories** | `app/repositories/` | Database queries & data-access abstraction                 |
| **Models**     | `app/models/`         | SQLAlchemy ORM table definitions                           |
| **Config**     | `app/config.py`       | Environment settings via Pydantic `BaseSettings`           |
| **Database**   | `app/database.py`     | Engine, session factory, and DB initialization             |

---

## Folder Structure

```
personal_budget_tracker/
├── .gitignore                  # Git ignore rules
├── README.md                   # Project documentation (this file)
├── requirements.txt            # Python dependencies
├── budget_tracker.db           # SQLite database (auto-created, git-ignored)
│
├── app/                        # Application package
│   ├── __init__.py             # Exports the FastAPI app instance
│   ├── main.py                 # FastAPI app setup, router registration, startup events
│   ├── config.py               # Pydantic settings (reads from .env)
│   ├── database.py             # SQLAlchemy engine, session, Base, init_db()
│   ├── dependencies.py         # JWT auth: get_current_user / get_current_active_user
│   │
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── __init__.py         # Re-exports all models
│   │   ├── category.py         # Category model (id, name, type)
│   │   ├── transaction.py      # Transaction model (amount, date, type, category FK)
│   │   ├── budget.py           # Budget model (category FK, amount, month, year)
│   │   └── user.py             # User model (email, hashed_password, is_active)
│   │
│   ├── schemas/                # Pydantic request/response schemas
│   │   ├── __init__.py         # Re-exports all schemas
│   │   ├── auth.py             # UserCreate, UserLogin, UserResponse, Token, TokenData
│   │   ├── category.py         # CategoryCreate, CategoryUpdate, CategoryResponse
│   │   ├── transaction.py      # TransactionCreate/Update/Response, TransactionFilter
│   │   ├── budget.py           # BudgetCreate, BudgetUpdate, BudgetResponse
│   │   └── ml.py               # OverspendingAlert, BudgetRecommendation, AlertResponse
│   │
│   ├── repositories/           # Data-access layer (database queries)
│   │   ├── __init__.py         # Re-exports repositories
│   │   ├── category_repository.py   # CRUD for categories
│   │   └── transaction_repository.py # CRUD + filters + aggregations for transactions
│   │
│   ├── services/               # Business logic layer
│   │   ├── __init__.py         # Re-exports services
│   │   ├── auth_service.py     # Password hashing, JWT tokens, user CRUD
│   │   ├── transaction_service.py # Transaction validation & CRUD orchestration
│   │   ├── budget_service.py   # Budget validation, status tracking, spend calculation
│   │   ├── report_service.py   # Financial summaries, category breakdowns, trends
│   │   └── ml_service.py       # ML-powered budget recommendations & overspending alerts
│   │
│   └── routers/                # API route handlers (FastAPI APIRouter)
│       ├── __init__.py         # Re-exports all routers
│       ├── auth.py             # POST /auth/register, POST /auth/login
│       ├── categories.py       # CRUD endpoints for /categories
│       ├── transactions.py     # CRUD + filter endpoints for /transactions
│       ├── budgets.py          # CRUD + status endpoints for /budgets
│       ├── reports.py          # GET /reports/summary, income/expenses by category
│       └── ml.py               # GET /ml/recommend, GET /ml/alerts
│
└── venv/                       # Python virtual environment (git-ignored)
```

---

## API Endpoints

### Authentication
| Method | Endpoint               | Description          |
|--------|------------------------|----------------------|
| POST   | `/api/v1/auth/register`| Register a new user  |
| POST   | `/api/v1/auth/login`   | Login, receive JWT   |

### Categories
| Method | Endpoint                         | Description                  |
|--------|----------------------------------|------------------------------|
| POST   | `/api/v1/categories`             | Create a category            |
| GET    | `/api/v1/categories`             | List all categories          |
| GET    | `/api/v1/categories/{id}`        | Get a category by ID         |
| GET    | `/api/v1/categories/type/{type}` | Filter by income/expense     |
| PUT    | `/api/v1/categories/{id}`        | Update a category            |
| DELETE | `/api/v1/categories/{id}`        | Delete a category            |

### Transactions
| Method | Endpoint                         | Description                    |
|--------|----------------------------------|--------------------------------|
| POST   | `/api/v1/transactions`           | Create a transaction           |
| GET    | `/api/v1/transactions`           | List/filter transactions       |
| GET    | `/api/v1/transactions/{id}`      | Get a transaction by ID        |
| PUT    | `/api/v1/transactions/{id}`      | Update a transaction           |
| DELETE | `/api/v1/transactions/{id}`      | Delete a transaction           |

### Budgets
| Method | Endpoint                                              | Description                    |
|--------|-------------------------------------------------------|--------------------------------|
| POST   | `/api/v1/budgets`                                     | Create a budget                |
| GET    | `/api/v1/budgets`                                     | List all budgets               |
| GET    | `/api/v1/budgets/{id}`                                | Get a budget by ID             |
| GET    | `/api/v1/budgets/month/{m}/year/{y}`                  | Budgets for a given month/year |
| GET    | `/api/v1/budgets/status/category/{id}/month/{m}/year/{y}` | Budget status for a category |
| PUT    | `/api/v1/budgets/{id}`                                | Update a budget                |
| DELETE | `/api/v1/budgets/{id}`                                | Delete a budget                |

### Reports & Dashboard
| Method | Endpoint                               | Description                                         |
|--------|----------------------------------------|-----------------------------------------------------|
| GET    | `/api/v1/reports/summary`              | Financial summary (dates optional, defaults to month) |
| GET    | `/api/v1/reports/dashboard`            | Aggregated dashboard summary (income, expenses, etc.)|
| GET    | `/api/v1/dashboard`                    | Direct dashboard overview endpoint                  |
| GET    | `/api/v1/reports/income-by-category`   | Income breakdown by category                        |
| GET    | `/api/v1/reports/expenses-by-category` | Expense breakdown by category                       |
| GET    | `/api/v1/reports/monthly-summary/{year}` | Monthly income/expense/net for year (optional year)|
| GET    | `/api/v1/reports/top-spending-categories` | Top spending categories                          |

### ML Insights
| Method | Endpoint                | Description                              |
|--------|-------------------------|------------------------------------------|
| GET    | `/api/v1/ml/recommend`  | ML-powered budget recommendations        |
| GET    | `/api/v1/ml/alerts`     | Overspending alerts for a given month    |

---

## Getting Started

### 1. Set Up Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Environment Variables

Create an `app/.env` file:
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
