from __future__ import annotations

from datetime import date
import random

from src.server.config import get_settings
from src.server.services.wallet_sync.providers import create_sandbox_transactions, exchange_plaid_public_token, _http_post_json


def create_sandbox_access_token() -> str:
    settings = get_settings()
    env = settings.PLAID_ENV or "sandbox"
    base_url = f"https://{env}.plaid.com"

    payload = {
        "client_id": settings.PLAID_CLIENT_ID,
        "secret": settings.PLAID_SECRET,
        "institution_id": "ins_109508",
        "initial_products": ["transactions"],
        "options": {
            "override_username": "user_transactions_dynamic",
            "override_password": "pass_good",
        },
    }
    data = _http_post_json(f"{base_url}/sandbox/public_token/create", payload, timeout=15)
    public_token = str(data.get("public_token") or "").strip()
    if not public_token:
        raise RuntimeError("Failed to create sandbox public token")

    exchange = exchange_plaid_public_token(public_token)
    access_token = str(exchange.get("access_token") or "").strip()
    if not access_token:
        raise RuntimeError("Failed to exchange public token for access token")
    return access_token


def build_12m_transactions() -> list[dict]:
    today = date.today()
    rng = random.Random(42)
    records: list[dict] = []

    for offset in range(11, -1, -1):
        year = today.year
        month = today.month - offset
        while month <= 0:
            month += 12
            year -= 1

        txn_date = date(year, month, 8).isoformat()
        salary = round(-1 * (4800 + rng.random() * 900), 2)
        expenses = round(3200 + rng.random() * 900, 2)

        records.append(
            {
                "amount": salary,
                "date_posted": txn_date,
                "date_transacted": txn_date,
                "description": f"Salary {year}-{month:02d}",
            }
        )
        records.append(
            {
                "amount": expenses,
                "date_posted": txn_date,
                "date_transacted": txn_date,
                "description": f"Expenses {year}-{month:02d}",
            }
        )

    return records


def seed_transactions(access_token: str) -> None:
    transactions = build_12m_transactions()
    for idx in range(0, len(transactions), 10):
        chunk = transactions[idx : idx + 10]
        create_sandbox_transactions(access_token=access_token, transactions=chunk)


def main() -> None:
    token = create_sandbox_access_token()
    seed_transactions(token)
    print("Seeded 12 months of Plaid sandbox transactions successfully.")
    print("Use this access_token in connect flow for demo item:")
    print(token)


if __name__ == "__main__":
    main()
