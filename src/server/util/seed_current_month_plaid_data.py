from __future__ import annotations

from datetime import date

from src.server.config import get_settings
from src.server.db.database import SessionLocal
from src.server.db.tables.user import User
from src.server.db.tables.wallet import AccountProvider
from src.server.services.financial_analysis.dashboard_metrics import DashboardMetricsService
from src.server.services.wallet_sync.providers import _http_post_json, create_sandbox_transactions, exchange_plaid_public_token
from src.server.services.wallet_sync.sync_service import SyncService


def create_dynamic_sandbox_access_token() -> tuple[str, str]:
    settings = get_settings()
    env = settings.PLAID_ENV or "sandbox"
    base_url = f"https://{env}.plaid.com"

    payload = {
        "client_id": settings.PLAID_CLIENT_ID,
        "secret": settings.PLAID_SECRET,
        "institution_id": "ins_109508",
        "initial_products": ["transactions", "investments", "liabilities"],
        "options": {
            "override_username": "user_transactions_dynamic",
            "override_password": "pass_good",
        },
    }
    data = _http_post_json(f"{base_url}/sandbox/public_token/create", payload, timeout=20)
    public_token = str(data.get("public_token") or "").strip()
    if not public_token:
        raise RuntimeError("Failed to create sandbox public token")

    exchange = exchange_plaid_public_token(public_token)
    access_token = str(exchange.get("access_token") or "").strip()
    item_id = str(exchange.get("item_id") or "").strip()
    if not access_token or not item_id:
        raise RuntimeError("Failed to exchange sandbox token")
    return access_token, item_id


def main() -> int:
    db = SessionLocal()
    user_id = 0
    access_token = ""
    sync_connection_id = 0
    try:
        user = db.query(User).filter(User.email == "demo@wwh.app").first()
        if not user:
            print("demo user not found")
            return 1
        user_id = int(getattr(user, "id"))

        access_token, item_id = create_dynamic_sandbox_access_token()
        connections = SyncService.connect_account(
            db=db,
            user=user,
            provider="plaid",
            account_type="bank",
            credentials={
                "accessToken": access_token,
                "itemId": item_id,
                "name": "Sandbox Dynamic Transactions",
            },
        )
        connection = connections[0]
        sync_connection_id = int(getattr(connection, "id"))

        today = date.today().isoformat()

        # Negative = income, positive = expense (matches existing accounting flow classifier).
        transactions = [
            {
                "amount": -5200.00,
                "date_posted": today,
                "date_transacted": today,
                "description": "Salary Payroll Current Month",
            },
            {
                "amount": -350.00,
                "date_posted": today,
                "date_transacted": today,
                "description": "Bonus Current Month",
            },
            {
                "amount": 1380.50,
                "date_posted": today,
                "date_transacted": today,
                "description": "Rent Current Month",
            },
            {
                "amount": 210.75,
                "date_posted": today,
                "date_transacted": today,
                "description": "Utilities Current Month",
            },
            {
                "amount": 128.30,
                "date_posted": today,
                "date_transacted": today,
                "description": "Groceries Current Month",
            },
        ]

        create_sandbox_transactions(access_token=access_token, transactions=transactions)

        sync_job = SyncService.create_sync_job(
            db=db,
            user_id=user_id,
            account_id=sync_connection_id,
            mode="quick",
        )
        sync_job_id = int(getattr(sync_job, "id"))
    finally:
        db.close()

    SyncService.run_sync_job(sync_job_id)

    db = SessionLocal()
    try:
        totals = DashboardMetricsService.build_totals(db=db, user_id=user_id)
        income_month = DashboardMetricsService.build_accounting_current_month(db=db, user_id=user_id, flow="income")
        expense_month = DashboardMetricsService.build_accounting_current_month(db=db, user_id=user_id, flow="expense")

        print("seeded_transactions", len(transactions))
        print("seeded_connection_id", sync_connection_id)
        print("sync_job_id", sync_job_id)
        print("total_income_12m", totals.get("total_income"))
        print("total_expense_12m", totals.get("total_expense"))
        print("current_month_income", income_month.get("total"), "count", income_month.get("count"))
        print("current_month_expense", expense_month.get("total"), "count", expense_month.get("count"))

    finally:
        db.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
