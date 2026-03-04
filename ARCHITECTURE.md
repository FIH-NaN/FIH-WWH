# Wealth Wellness Hub - Full Architecture

## Project Structure

```
nan/
├── src/
│   ├── entities/                      # Python domain models (shared)
│   │   ├── assets.py                  # Asset classes
│   │   ├── liabilities.py             # Liability classes
│   │   ├── incomes.py                 # Income classes
│   │   ├── expenses.py                # Expense classes
│   │   ├── cash_flows.py              # Cash flow models
│   │   └── wallet.py                  # Wallet aggregate
│   │
│   ├── server/                        # FastAPI Backend
│   │   ├── main.py                    # FastAPI entry point
│   │   ├── config.py                  # Settings management
│   │   ├── database.py                # SQLAlchemy setup
│   │   ├── models.py                  # ORM models (User, Asset, Transaction, Category)
│   │   ├── schemas.py                 # Pydantic validation schemas
│   │   ├── requirements.txt           # Python dependencies
│   │   ├── .env.example               # Environment template
│   │   ├── README.md                  # Server documentation
│   │   │
│   │   ├── core/
│   │   │   └── security.py            # JWT & password utilities
│   │   │
│   │   ├── routers/
│   │   │   ├── auth.py                # Auth endpoints (register, login, me)
│   │   │   ├── assets.py              # Asset CRUD & analytics
│   │   │   ├── transactions.py        # Transaction CRUD & import
│   │   │   └── categories.py          # Category management
│   │   │
│   │   └── entities/                  # Domain models (shared reference)
│   │
│   ├── web/                           # React Frontend
│   │   ├── src/
│   │   │   ├── App.tsx                # Main dashboard component
│   │   │   ├── App.css                # Dashboard styles
│   │   │   └── index.css              # Global styles
│   │   ├── package.json               # npm dependencies (React, Vite)
│   │   └── tsconfig.json              # TypeScript config
│   │
│   ├── assets.py                      # Original entities (moved to server)
│   └── schema.sql                     # SQLite schema definition
│
├── FIH-WWH.md                         # API specification document
└── README.md                          # Main project readme
```

## Technology Stack

### Backend
- **Framework**: FastAPI (async Python web framework)
- **Database**: SQLite + SQLAlchemy ORM
- **Authentication**: JWT (python-jose) + BCrypt
- **Validation**: Pydantic v2
- **Server**: Uvicorn ASGI server

### Frontend
- **Framework**: React 19
- **Build Tool**: Vite
- **Language**: TypeScript
- **Styling**: Pure CSS (no framework)

### Shared Domain Models
- Python dataclasses in `src/entities/`
- Covers assets, liabilities, incomes, expenses, cash flows, wallet

## API Endpoints

### Authentication
```
POST   /auth/register      - Register new user
POST   /auth/login         - Login user
GET    /auth/me            - Get current user info
```

### Assets
```
GET    /assets             - List assets (with filters, pagination)
POST   /assets             - Create asset
GET    /assets/{id}        - Get single asset
PUT    /assets/{id}        - Update asset
DELETE /assets/{id}        - Delete asset
GET    /assets/summary     - Asset portfolio summary
GET    /assets/distribution - Asset distribution by type
GET    /assets/health-score - Health score & grade
```

### Transactions
```
GET    /transactions                   - List transactions (with date/type filters)
POST   /transactions                   - Create transaction
POST   /transactions/import            - Batch import transactions
```

### Categories
```
GET    /categories         - List user categories
POST   /categories         - Create category
```

## Dashboard UI

Single-page React dashboard displaying:
- **KPI Strip**: Total assets, liabilities, monthly income/expense, net cash flow
- **Assets Table**: Holdings with category, liquidity status, values
- **Asset Distribution**: Mini bar chart by category
- **Liabilities Table**: Debt obligations with monthly payments
- **Income Table**: Income sources and monthly amounts
- **Expense Table**: Spending by category with essential flag
- **Expense Distribution**: Mini bar chart by category
- **Recent Cash Flows**: Transaction history with inflow/outflow tags

## Development & Deployment

### Quick Start

**Backend**:
```bash
cd src/server
python main.py  # Runs on http://localhost:8000
```

**Frontend**:
```bash
cd src/web
npm install
npm run dev     # Runs on http://localhost:5173
```

### Database

- Auto-initialized on first server run
- SQLite file stored as `wealth_hub.db`
- Schema defined in `src/entities/schema.sql`

### Authentication Flow

1. User registers via `/auth/register`
2. Server returns JWT token
3. Client stores token in session
4. All subsequent requests include token (query param or header)
5. Server validates JWT and checks user ownership of resources

## Design Philosophy

- **Separation of Concerns**: Core domain logic in `entities/`, HTTP layer in `routers/`
- **Type Safety**: Python type hints + Pydantic validation + TypeScript
- **DRY**: Shared entity models between backend and frontend documentation
- **Stateless**: JWT-based auth enables horizontal scaling
- **Simplicity**: No external UI framework, pure CSS for maximum control
- **API-First**: Clear contract defined before implementation

## Key Features Implemented

✓ User registration & JWT authentication
✓ Asset CRUD with type-based classification
✓ Asset portfolio analytics (summary, distribution, health score)
✓ Transaction tracking and batch import
✓ Custom category management
✓ Responsive dashboard with inline visualization
✓ Currency & timezone awareness
✓ Comprehensive error handling

## Next Steps

- [ ] Connect React frontend to FastAPI backend
- [ ] Add real-time price updates for crypto/stocks
- [ ] Implement advanced filtering and search
- [ ] Add data export (CSV, PDF)
- [ ] Add scenario-based "what-if" analysis
- [ ] Implement goal tracking
- [ ] Add multi-currency support with conversion
