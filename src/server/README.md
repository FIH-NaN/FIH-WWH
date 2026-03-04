# Wealth Wellness Hub - Backend Server

A FastAPI-based backend server implementing the FIH-WWH (Wealth Wellness Hub) API specification.

## Directory Structure

```
server/
├── main.py                  # FastAPI application entry point
├── config.py                # Configuration and settings management
├── database.py              # SQLAlchemy setup and ORM session management
├── models.py                # SQLAlchemy ORM models (User, Asset, Transaction, Category)
├── schemas.py               # Pydantic request/response validation schemas
├── requirements.txt         # Python dependencies
├── .env.example              # Environment variables template
│
├── core/                    # Core utilities and security
│   ├── __init__.py
│   ├── security.py          # JWT & password hashing utilities
│   └── dependencies.py      # Shared auth dependency (current user)
│
├── routers/                 # API endpoint handlers organized by domain
│   ├── __init__.py
│   ├── auth.py              # Authentication endpoints (register, login, me)
│   ├── assets.py            # Asset management endpoints
│   ├── accounts.py          # Connected account endpoints
│   ├── transactions.py      # Transaction endpoints
│   ├── categories.py        # Category endpoints
│   └── scheduler.py         # Background scheduler control endpoints

├── services/                # Business logic services
│   ├── account_service.py
│   ├── asset_analytics_service.py
│   └── health_scoring_service.py
│
└── entities/                # Domain models (from Python backend)
    ├── __init__.py
    ├── assets.py
    ├── liabilities.py
    ├── incomes.py
    ├── expenses.py
    ├── cash_flows.py
    └── wallet.py
```

## Setup & Installation

### 1. Configure Environment

Copy `.env.example` to `.env` and update values:

```bash
cp .env.example .env
```

Edit `.env` with your settings:
- Change `SECRET_KEY` to a secure random string
- Update `DATABASE_URL` if not using SQLite
- Set `CORS_ORIGINS` for your frontend URL

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Or if already in virtual environment with packages installed:

```bash
pip install -e .
```

### 3. Initialize Database

The database is automatically initialized on first app run, but you can manually create tables:

```bash
python -c "from database import init_db; init_db()"
```

### 4. Run Development Server

```bash
python main.py
```

Or use uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Architecture

### Authentication (`routers/auth.py`)
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user info

### Assets (`routers/assets.py`)
- `GET /assets` - List user assets
- `POST /assets` - Create new asset
- `GET /assets/{id}` - Get single asset
- `PUT /assets/{id}` - Update asset
- `DELETE /assets/{id}` - Delete asset
- `GET /assets/summary` - Get asset summary
- `GET /assets/distribution` - Get asset distribution
- `GET /assets/health-score` - Get health score

### Transactions (`routers/transactions.py`)
- `GET /transactions` - List transactions
- `POST /transactions` - Create transaction
- `POST /transactions/import` - Batch import transactions

### Categories (`routers/categories.py`)
- `GET /categories` - List categories
- `POST /categories` - Create category

### Accounts (`routers/accounts.py`)
- `GET /accounts` - List connected accounts
- `POST /accounts/connect` - Connect account
- `POST /accounts/sync` - Sync account and return next actions
- `DELETE /accounts?id={id}` - Disconnect account

### Scheduler (`routers/scheduler.py`)
- `GET /scheduler/jobs` - List scheduled jobs
- `POST /scheduler/jobs/{job_id}/trigger` - Trigger job now
- `DELETE /scheduler/jobs/{job_id}` - Remove scheduled job
- `GET /scheduler/status` - Get scheduler runtime status

## Database Models

### User
- `id`: Primary key
- `email`: Unique user email
- `name`: User display name
- `hashed_password`: BCrypt hashed password
- `created_at`, `updated_at`: Timestamps

### Asset
- `id`: Primary key
- `user_id`: Foreign key to User
- `name`: Asset name
- `asset_type`: Enum (cash, stock, fund, crypto, property, other)
- `value`: Current asset value
- `currency`: Asset currency code
- `category`: User-defined category
- `description`: Optional notes
- `created_at`, `updated_at`: Timestamps

### Transaction
- `id`: Primary key
- `user_id`: Foreign key to User
- `asset_id`: Foreign key to Asset
- `transaction_type`: Enum (income, expense)
- `amount`: Transaction amount
- `category`: Transaction category
- `description`: Optional notes
- `transaction_date`: When transaction occurred
- `created_at`, `updated_at`: Timestamps

### Category
- `id`: Primary key
- `user_id`: Foreign key to User
- `name`: Category name
- `category_type`: "asset" or "transaction"
- `icon`: Optional icon name/emoji
- `created_at`, `updated_at`: Timestamps

## Authentication

All endpoints (except `/auth/register` and `/auth/login`) require a valid JWT token. Preferred mode is `Authorization: Bearer <token>`; query token fallback is retained for compatibility:

```bash
# Preferred Authorization header
curl -H "Authorization: Bearer eyJhb..." http://localhost:8000/assets

# Compatibility query parameter
curl "http://localhost:8000/assets?token=eyJhb..."
```

Tokens are valid for 30 minutes (configurable in `.env`).

## Response Format

All responses follow a consistent format:

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional message"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error type",
  "message": "Detailed error message"
}
```

## Development Notes

- **Database**: SQLite by default (auto-created on first run)
- **ORM**: SQLAlchemy 2.0 with relationship mappings
- **Validation**: Pydantic v2 with custom error handling
- **JWT**: python-jose with HS256 algorithm
- **Password Hashing**: pbkdf2_sha256

## Future Improvements

- [ ] Add pagination helpers for list endpoints
- [ ] Implement asset valuation snapshots
- [ ] Add transaction filtering and search
- [ ] Implement dashboard metrics aggregation
- [ ] Add file upload for bulk transactions
- [ ] Implement rate limiting
- [ ] Add request logging and monitoring
