# Wealth Wellness Hub (WWH)

Wealth Wellness Hub is a full-stack personal finance platform that unifies:
- Traditional finance data (Plaid bank/investment accounts)
- On-chain wallet holdings (EVM networks)
- Accounting analytics (income, expense, budgets, trends)
- Portfolio analytics (assets, liabilities, holdings distribution, market indicators)
- AI-powered insights and advisor chat

## Live Deployment
- WWH URL: https://elect-coffee-exchange-spell.trycloudflare.com

## Tech Stack
- Frontend: React + Vite + TypeScript + Tailwind CSS + Recharts
- Backend: FastAPI + SQLAlchemy + SQLite
- Data Integrations: Plaid Sandbox, EVM wallet connectors, Yahoo market data
- AI: MiniMax-compatible chat/insight generation
- Deployment: Docker Compose + Nginx reverse proxy

## Key Product Modules
- Dashboard
  - Net worth, total income, total expenses, savings rate
  - Balance Sheet and Income Statement
  - Budget configuration and persistence by month
  - AI insight panel
- My Assets
  - Connect MetaMask / EVM wallets
  - Connect Plaid bank accounts
  - One-click "Seed Plaid Demo Data" for reliable hackathon demos
  - Wallet cards and holdings drill-down
- Accounting
  - Current-month income and expense ledgers
  - 12-month trend analysis
  - Budget editing and save
- Portfolio
  - Assets and liabilities summary
  - Investment holdings donut + detailed legend
  - Market indicators grouped by Macro Core, Multi Asset, and Risk Pulse
- AI Advisor
  - Deterministic factor breakdown
  - Cached/live AI recommendations
  - DB-backed multi-turn advisor chat

## Local Development

### Backend
```bash
cd src/server
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m src.server.main
```

Backend runs on `http://localhost:8080`.

### Frontend
```bash
cd src/web
npm install
npm run dev
```

Frontend runs on `http://localhost:5173`.

## Docker Deployment
```bash
docker compose --env-file .env.docker up -d --build
```

Default Docker entrypoint:
- Frontend (Nginx): `http://localhost`
- Backend API via proxy: `http://localhost/api/...`

## Environment Variables (Important)
Set these before production usage:
- `SECRET_KEY`
- `PLAID_CLIENT_ID`
- `PLAID_SECRET`
- `PLAID_ENV`
- `PLAID_TOKEN_ENCRYPTION_KEY`
- `MINIMAX_API_KEY`
- `GOLDRUSH_API_KEY`

## Notes for Hackathon Demo
- Use the `Seed Plaid Demo Data` button in **My Assets** to guarantee non-zero accounting data.
- Use manual `Sync Active Wallet` after account connection for deterministic refresh timing.
- Market indicators include anti-rate-limit fallback behavior for demo stability.
