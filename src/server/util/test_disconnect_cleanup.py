import time

import requests
from fastapi.testclient import TestClient

from src.server.config import get_settings
from src.server.main import app


def main() -> int:
    client = TestClient(app)
    email = f"disconnect_fix_{int(time.time())}@example.com"
    reg = client.post(
        "/auth/register",
        json={"email": email, "name": "Disconnect Fix", "password": "Passw0rd!"},
    )
    if reg.status_code != 200:
        print("register failed", reg.status_code, reg.text)
        return 1

    token = reg.json()["data"]["token"]
    headers = {"Authorization": f"Bearer {token}"}

    settings = get_settings()
    pt_resp = requests.post(
        "https://sandbox.plaid.com/sandbox/public_token/create",
        json={
            "client_id": settings.PLAID_CLIENT_ID,
            "secret": settings.PLAID_SECRET,
            "institution_id": "ins_109508",
            "initial_products": ["auth", "transactions", "investments"],
        },
        timeout=25,
    )
    pt_resp.raise_for_status()
    public_token = pt_resp.json().get("public_token")

    connect = client.post(
        "/accounts/connect",
        headers=headers,
        json={
            "provider": "plaid",
            "type": "bank",
            "credentials": {"publicToken": public_token, "name": "Tmp"},
        },
    )
    if connect.status_code != 200:
        print("connect failed", connect.status_code, connect.text)
        return 1

    account_id = connect.json()["data"]["accounts"][0]["id"]
    sync = client.post("/accounts/sync", headers=headers, json={"account_id": account_id, "mode": "quick"})
    if sync.status_code != 200:
        print("sync trigger failed", sync.status_code, sync.text)
        return 1

    job_id = sync.json()["data"]["job_id"]
    final_status = None
    for _ in range(60):
        status = client.get(f"/accounts/sync/{job_id}", headers=headers)
        if status.status_code == 200:
            final_status = status.json().get("data", {})
            if final_status.get("status") in {"success", "failed"}:
                break
        time.sleep(1)

    before = client.get("/dashboard/summary", headers=headers).json().get("data", {})
    client.delete(f"/accounts?id={account_id}", headers=headers)
    after = client.get("/dashboard/summary", headers=headers).json().get("data", {})

    print("sync_status", final_status.get("status") if isinstance(final_status, dict) else None)
    print("before", before.get("total_income"), before.get("total_expense"), before.get("net_worth"))
    print("after", after.get("total_income"), after.get("total_expense"), after.get("net_worth"))
    print("disconnect_status_ok", after.get("total_income", 0) == 0 and after.get("total_expense", 0) == 0)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
