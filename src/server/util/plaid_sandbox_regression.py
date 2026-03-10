import json
import sys
import time
from typing import Any, Dict, List

import requests
from fastapi.testclient import TestClient

from src.server.config import get_settings
from src.server.db.database import SessionLocal
from src.server.db.tables.plaid_liabilities import PlaidLiability
from src.server.db.tables.plaid_transactions import PlaidTransaction
from src.server.db.tables.user import User
from src.server.db.tables.wallet import AccountConnection, ExternalHolding
from src.server.main import app


def ok(item: str, passed: bool, detail: str) -> Dict[str, Any]:
    return {"item": item, "passed": passed, "detail": detail}


def create_sandbox_public_token() -> str:
    settings = get_settings()
    if not settings.PLAID_CLIENT_ID or not settings.PLAID_SECRET:
        raise RuntimeError("PLAID_CLIENT_ID/PLAID_SECRET missing")

    payload = {
        "client_id": settings.PLAID_CLIENT_ID,
        "secret": settings.PLAID_SECRET,
        "institution_id": "ins_109508",
        "initial_products": ["auth", "transactions", "investments"],
    }

    resp = requests.post("https://sandbox.plaid.com/sandbox/public_token/create", json=payload, timeout=20)
    resp.raise_for_status()
    body = resp.json()
    token = str(body.get("public_token") or "").strip()
    if not token:
        raise RuntimeError(f"No public_token returned: {body}")
    return token


def expect_fields(obj: Dict[str, Any], required: List[str]) -> List[str]:
    return [key for key in required if key not in obj]


def main() -> int:
    checks: List[Dict[str, Any]] = []

    try:
        public_token = create_sandbox_public_token()
        checks.append(ok("plaid.sandbox_public_token", True, "public_token created"))
    except Exception as exc:
        checks.append(ok("plaid.sandbox_public_token", False, str(exc)))
        print(json.dumps({"checks": checks}, indent=2, ensure_ascii=False))
        return 2

    client = TestClient(app)
    email = f"plaid_reg_{int(time.time())}@example.com"
    reg = client.post("/auth/register", json={"email": email, "name": "Plaid Regression", "password": "Passw0rd!"})
    if reg.status_code != 200:
        checks.append(ok("api.auth.register", False, reg.text))
        print(json.dumps({"checks": checks}, indent=2, ensure_ascii=False))
        return 1

    token = reg.json()["data"]["token"]
    headers = {"Authorization": f"Bearer {token}"}
    checks.append(ok("api.auth.register", True, "user created"))

    connect = client.post(
        "/accounts/connect",
        headers=headers,
        json={
            "provider": "plaid",
            "type": "bank",
            "credentials": {
                "publicToken": public_token,
                "name": "Sandbox Regression Account",
            },
        },
    )
    if connect.status_code != 200:
        checks.append(ok("api.accounts.connect", False, connect.text))
        print(json.dumps({"checks": checks}, indent=2, ensure_ascii=False))
        return 1

    accounts = connect.json().get("data", {}).get("accounts", [])
    account_id = accounts[0]["id"] if accounts else None
    checks.append(ok("api.accounts.connect", account_id is not None, f"linked_accounts={len(accounts)}"))
    if account_id is None:
        print(json.dumps({"checks": checks}, indent=2, ensure_ascii=False))
        return 1

    sync = client.post("/accounts/sync", headers=headers, json={"account_id": account_id, "mode": "quick"})
    if sync.status_code != 200:
        checks.append(ok("api.accounts.sync.trigger", False, sync.text))
        print(json.dumps({"checks": checks}, indent=2, ensure_ascii=False))
        return 1

    job_id = sync.json().get("data", {}).get("job_id")
    final_status = None
    for _ in range(40):
        status_resp = client.get(f"/accounts/sync/{job_id}", headers=headers)
        if status_resp.status_code != 200:
            time.sleep(1)
            continue
        final_status = status_resp.json().get("data", {})
        if final_status.get("status") in {"success", "failed"}:
            break
        time.sleep(1)

    if not final_status:
        checks.append(ok("api.accounts.sync.status", False, "sync status polling timed out"))
        print(json.dumps({"checks": checks}, indent=2, ensure_ascii=False))
        return 1

    sync_ok = final_status.get("status") == "success"
    checks.append(ok("api.accounts.sync.status", sync_ok, json.dumps(final_status, ensure_ascii=False)))

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            checks.append(ok("db.user.lookup", False, "user not found"))
            print(json.dumps({"checks": checks}, indent=2, ensure_ascii=False))
            return 1

        user_id = int(getattr(user, "id"))
        holdings = db.query(ExternalHolding).filter(ExternalHolding.user_id == user_id).all()
        txns = db.query(PlaidTransaction).filter(PlaidTransaction.user_id == user_id, PlaidTransaction.is_removed == False).all()  # noqa: E712
        liabilities = db.query(PlaidLiability).filter(PlaidLiability.user_id == user_id).all()

        checks.append(ok("db.external_holdings.count", len(holdings) > 0, f"count={len(holdings)}"))
        checks.append(ok("db.plaid_transactions.count", len(txns) > 0, f"count={len(txns)}"))
        checks.append(ok("db.plaid_liabilities.count", len(liabilities) >= 0, f"count={len(liabilities)}"))

        if holdings:
            sample = holdings[0]
            checks.append(ok("db.external_holdings.fields", bool(getattr(sample, "external_holding_id", None)) and float(getattr(sample, "value_usd") or 0) >= 0, "external_holding_id/value_usd"))
        if txns:
            sample_txn = txns[0]
            checks.append(ok("db.plaid_transactions.fields", bool(getattr(sample_txn, "transaction_id", None)) and getattr(sample_txn, "date_posted", None) is not None, "transaction_id/date_posted"))
        if liabilities:
            sample_liab = liabilities[0]
            checks.append(ok("db.plaid_liabilities.fields", bool(getattr(sample_liab, "account_id", None)) and str(getattr(sample_liab, "liability_type", "")) in {"credit", "loan"}, "account_id/liability_type"))

    finally:
        db.close()

    api_expectations = {
        "/dashboard/summary": ["net_worth", "total_income", "total_expense", "savings_rate", "balance_sheet", "income_statement"],
        "/dashboard/balance-sheet": ["net_worth", "assets", "liabilities"],
        "/dashboard/income-statement": ["income_items", "expense_items", "remaining_balance"],
        "/accounting/current-month?flow=income": ["transactions", "count", "total"],
        "/accounting/series-12m?flow=expense": ["data", "average"],
        "/portfolio/summary": ["net_worth", "assets", "liabilities"],
        "/market/indicators": ["groups", "indicators"],
    }

    for path, required in api_expectations.items():
        resp = client.get(path, headers=headers)
        if resp.status_code != 200:
            checks.append(ok(f"api{path}", False, f"status={resp.status_code}"))
            continue
        data = resp.json().get("data", {})
        missing = expect_fields(data, required)
        checks.append(ok(f"api{path}.fields", len(missing) == 0, f"missing={missing}"))

    result = {"checks": checks}
    print(json.dumps(result, indent=2, ensure_ascii=False))

    failed = [item for item in checks if not item["passed"]]
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
