from src.server.db.database import SessionLocal
from src.server.db.tables.plaid_liabilities import PlaidLiability
from src.server.db.tables.plaid_transactions import PlaidTransaction
from src.server.db.tables.wallet import AccountConnection


def main() -> int:
    db = SessionLocal()
    try:
        existing_ids = {int(row.id) for row in db.query(AccountConnection.id).all()}

        txns = db.query(PlaidTransaction).all()
        liabs = db.query(PlaidLiability).all()

        delete_txn_ids = [int(row.id) for row in txns if int(getattr(row, "account_connection_id") or 0) not in existing_ids]
        delete_liab_ids = [int(row.id) for row in liabs if int(getattr(row, "account_connection_id") or 0) not in existing_ids]

        removed_txn = 0
        removed_liab = 0
        if delete_txn_ids:
            removed_txn = db.query(PlaidTransaction).filter(PlaidTransaction.id.in_(delete_txn_ids)).delete(synchronize_session=False)
        if delete_liab_ids:
            removed_liab = db.query(PlaidLiability).filter(PlaidLiability.id.in_(delete_liab_ids)).delete(synchronize_session=False)

        db.commit()
        print(f"Removed orphan plaid transactions: {removed_txn}")
        print(f"Removed orphan plaid liabilities: {removed_liab}")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
