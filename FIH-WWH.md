---
title: Wealth Wellness Hub API (Current)
language_tabs:
  - shell: Shell
  - http: HTTP
  - javascript: JavaScript
toc_footers: []
includes: []
search: true
code_clipboard: true
highlight_theme: darkula
headingLevel: 2
---

# Wealth Wellness Hub API

## Deployment
- Public demo URL: https://elect-coffee-exchange-spell.trycloudflare.com
- API base (behind Nginx): `https://elect-coffee-exchange-spell.trycloudflare.com/api`

## Authentication
Bearer token is required for all protected endpoints.

Example header:
```http
Authorization: Bearer <JWT_TOKEN>
```

---

## Core Endpoint Groups

### Auth
- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`

### Assets and Insights
- `GET /assets`
- `POST /assets`
- `GET /assets/{asset_id}`
- `PUT /assets/{asset_id}`
- `DELETE /assets/{asset_id}`
- `GET /assets/summary`
- `GET /assets/distribution`
- `GET /assets/health-score`
- `GET /assets/wealth-overview`
- `GET /assets/wealth-overview/insights`
- `POST /assets/wealth-overview/insights/refresh`
- `GET /assets/wealth-overview/insights/history`
- `GET /assets/portfolio-analysis`

### Accounts, Plaid, Wallets, Sync
- `POST /accounts/connect`
- `GET /accounts/plaid/link-token`
- `GET /accounts`
- `DELETE /accounts?id={account_id}`
- `POST /accounts/sync`
- `GET /accounts/sync/{job_id}`
- `POST /accounts/plaid/seed-current-month-demo`
- `GET /accounts/wallets/summary`
- `GET /accounts/wallets/{account_id}/holdings`

### Analytics (Dashboard / Accounting / Portfolio / Market / Advisor Chat)
- `GET /dashboard/balance-sheet`
- `GET /dashboard/totals`
- `GET /dashboard/income-statement`
- `GET /dashboard/summary`
- `GET /dashboard/budgets`
- `PUT /dashboard/budgets`
- `GET /accounting/current-month?flow=income|expense`
- `GET /accounting/series-12m?flow=income|expense`
- `GET /portfolio/summary`
- `GET /portfolio/investment-holdings`
- `GET /market/indicators`
- `GET /advisor/chat/conversations`
- `GET /advisor/chat/conversations/{conversation_id}`
- `POST /advisor/chat/messages`

### Manual Transaction Endpoints
- `GET /transactions`
- `POST /transactions`
- `POST /transactions/import`

---

## Example Requests

### Register
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "demo@example.com",
  "name": "Demo User",
  "password": "Passw0rd!"
}
```

### Trigger Account Sync
```http
POST /api/accounts/sync
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "account_id": 11,
  "mode": "quick"
}
```

### Seed Plaid Demo Data (Hackathon Helper)
```http
POST /api/accounts/plaid/seed-current-month-demo
Authorization: Bearer <JWT_TOKEN>
```

### Market Indicators
```http
GET /api/market/indicators
Authorization: Bearer <JWT_TOKEN>
```

---

## Response Envelope

Successful responses follow:
```json
{
  "success": true,
  "data": {},
  "message": "optional"
}
```

Error responses use FastAPI HTTP error semantics with status code and `detail`.

---

## Demo Notes
- For deterministic accounting demo data, call `POST /accounts/plaid/seed-current-month-demo`.
- UI normally reads from DB-backed aggregates; sync is manual by design.
- Market indicator endpoint includes cache/fallback behavior for better resiliency during demos.
