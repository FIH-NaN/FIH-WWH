# Wealth Wellness Hub - Architecture

## Live Deployment
- Production demo URL: https://elect-coffee-exchange-spell.trycloudflare.com

## High-Level Architecture

WWH is a two-tier web application:
- Web Client (React/Vite)
- API Service (FastAPI)

Data is persisted in SQLite and refreshed through explicit sync flows.

```text
Browser (React)
   |
   | HTTPS (via Nginx)
   v
Nginx (static + /api proxy)
   |
   | HTTP
   v
FastAPI (routers/services)
   |
   +--> SQLite (users, assets, connections, holdings, transactions, budgets, chat)
   +--> Plaid APIs (accounts, investments, transactions, liabilities)
   +--> EVM providers (wallet holdings)
   +--> Yahoo market data (indicators)
   +--> MiniMax API (insights/chat)
```

## Repository Structure (Current)

```text
FIH-WWH/
 docker-compose.yml
 Dockerfile.backend
 Dockerfile.frontend
 deploy/
    nginx.conf
 src/
    server/
       main.py
       config.py
       db/
          database.py
          tables/
       routers/
          auth.py
          assets.py
          accounts.py
          transactions.py
          analytics.py
       services/
          wallet_sync/
          financial_analysis/
          user_data/
          auth/
       util/
    web/
        src/
            pages/
            services/
            layout/
            state/
            types/
 FIH-WWH.md
```

## Backend Design

### Router Layer
- `auth.py`: register/login/me
- `assets.py`: manual asset CRUD + wealth overview + insights + portfolio analysis
- `accounts.py`: connect/disconnect/sync/link-token/wallet summary/holdings + Plaid demo seed endpoint
- `transactions.py`: manual transaction CRUD/import
- `analytics.py`: dashboard/accounting/portfolio/market/advisor-chat APIs

### Service Layer
- `services/wallet_sync/`: provider adapters, sync orchestration, holdings/transactions/liabilities ingestion
- `services/financial_analysis/`: dashboard metrics, accounting aggregates, portfolio summaries, market indicators
- `services/user_data/`: user-facing business operations
- `services/auth/`: token/security helpers

### Data Layer
Core persisted entities include:
- Users and auth data
- Manual assets and transactions
- Account connections (Plaid/EVM) and credentials
- External holdings
- Plaid transactions and liabilities
- Budget items
- Advisor conversations/messages

## Frontend Design

### Routing
- `/dashboard`
- `/assets`
- `/accounting`
- `/portfolio`
- `/ai-advisor`
- `/settings`

### Data Access Pattern
- Frontend calls typed service functions (`src/web/src/services/*`)
- APIs return envelope shape `{ success, data, message }`
- Pages refresh from DB-backed endpoints
- Sync actions are user-triggered (not continuous polling)

## Sync and Refresh Strategy

1. User connects account/wallet.
2. User triggers sync (`quick` or `deep`).
3. Backend ingests and stores normalized data.
4. UI reloads from persisted DB aggregates.

This improves performance and demo reliability by avoiding dependency on every page load.

## Deployment Topology

### Docker Compose Services
- `backend`: FastAPI (port 8080 internally)
- `frontend`: Nginx serving SPA and proxying `/api` to backend

### Nginx Rules
- `/` -> serve built React app
- `/api/` -> proxy to `backend:8080`

## Reliability Notes
- Market indicators use cache + fallback behavior to tolerate rate limits.
- Plaid demo endpoint can seed current-month transactions for deterministic accounting demos.
- Sidebar is fixed on desktop while content scrolls independently.
