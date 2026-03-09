from datetime import datetime
import json
from typing import List, Optional

from sqlalchemy.orm import Session

from src.server.core.entities.assets import AssetCategory
from src.server.core.secrets import encrypt_secret
from src.server.db.database import SessionLocal
from src.server.db.db_gateway.assets import get_next_asset_id
from src.server.db.tables.assets import Asset
from src.server.db.tables.user import User
from src.server.db.tables.wallet import (
    AccountConnection,
    AccountCredential,
    AccountProvider,
    AccountType,
    ExternalHolding,
    SyncJob,
    SyncJobStatus,
)
from src.server.db.tables.plaid_transactions import PlaidTransaction
from src.server.services.wallet_sync.providers import (
    EvmHoldingsResult,
    ProviderError,
    exchange_plaid_public_token,
    fetch_evm_holdings,
    fetch_plaid_investment_holdings,
    fetch_plaid_holdings,
    fetch_plaid_transactions_sync,
    parse_transaction_date,
    serialize_payload,
    validate_evm_address,
)
from src.server.services.financial_analysis.wellness_metrics import WellnessMetricsService


class SyncService:
    @staticmethod
    def _enum_value(value: object) -> str:
        enum_value = getattr(value, "value", None)
        return str(enum_value) if enum_value is not None else str(value)

    @staticmethod
    def _resolve_asset_category(provider_value: str, connection_account_type: str, raw_payload: object) -> AssetCategory:
        if provider_value == AccountProvider.EVM.value:
            return AssetCategory.DIGITAL_ASSET

        if provider_value == AccountProvider.PLAID.value:
            if isinstance(raw_payload, dict):
                security_type = str(raw_payload.get("security_type") or "").strip().lower()
                security_subtype = str(raw_payload.get("security_subtype") or "").strip().lower()
                if security_type in {"fixed income", "fixed_income"} or security_subtype in {"bond", "bill"}:
                    return AssetCategory.BOND
                if security_type in {"equity", "etf", "mutual fund", "mutual_fund"}:
                    return AssetCategory.STOCK
                if security_type == "cash":
                    return AssetCategory.CASH
                if security_type == "cryptocurrency":
                    return AssetCategory.DIGITAL_ASSET

                account = raw_payload.get("account") if isinstance(raw_payload.get("account"), dict) else raw_payload
                plaid_type = str((account or {}).get("type") or "").strip().lower()
                if plaid_type in {"investment", "brokerage", "securities"}:
                    return AssetCategory.STOCK
                if plaid_type in {"depository", "cash", "bank"}:
                    return AssetCategory.CASH

            if connection_account_type == AccountType.BROKERAGE.value:
                return AssetCategory.STOCK
            return AssetCategory.CASH

        return AssetCategory.OTHER

    @staticmethod
    def connect_account(db: Session, user: User, provider: str, account_type: str, credentials: Optional[dict]) -> List[AccountConnection]:
        credentials = credentials or {}

        if provider == AccountProvider.EVM.value:
            wallet_address = (credentials.get("walletAddress") or "").strip()
            network = (credentials.get("network") or "ethereum").strip().lower()
            if not wallet_address or not validate_evm_address(wallet_address):
                raise ValueError("Invalid walletAddress. Expected a valid EVM address.")

            existing = db.query(AccountConnection).filter(
                AccountConnection.user_id == user.id,
                AccountConnection.provider == AccountProvider.EVM,
                AccountConnection.provider_account_id == wallet_address.lower(),
                AccountConnection.network == network,
            ).first()
            if existing:
                setattr(existing, "status", "active")
                setattr(existing, "last_error", None)
                db.commit()
                db.refresh(existing)
                return [existing]

            conn = AccountConnection(
                user_id=user.id,
                provider=AccountProvider.EVM,
                account_type=AccountType.CRYPTO_WALLET,
                provider_account_id=wallet_address.lower(),
                name=credentials.get("name") or f"{network.title()} Wallet {wallet_address[:6]}...{wallet_address[-4:]}",
                wallet_address=wallet_address.lower(),
                network=network,
                status="active",
            )
            db.add(conn)
            db.commit()
            db.refresh(conn)
            return [conn]

        if provider == AccountProvider.PLAID.value:
            access_token = credentials.get("accessToken")
            item_id = credentials.get("itemId")

            public_token = credentials.get("publicToken")
            if public_token and not access_token:
                exchange = exchange_plaid_public_token(public_token)
                access_token = exchange.get("access_token")
                item_id = exchange.get("item_id")

            if not access_token:
                raise ValueError("Plaid connect requires publicToken or accessToken.")

            provider_account_id = credentials.get("accountId") or item_id or access_token[-10:]
            existing = db.query(AccountConnection).filter(
                AccountConnection.user_id == user.id,
                AccountConnection.provider == AccountProvider.PLAID,
                AccountConnection.provider_account_id == provider_account_id,
            ).first()

            if existing:
                connection = existing
            else:
                connection = AccountConnection(
                    user_id=user.id,
                    provider=AccountProvider.PLAID,
                    account_type=AccountType.BANK,
                    provider_account_id=provider_account_id,
                    provider_item_id=item_id,
                    name=credentials.get("name") or "Plaid Linked Account",
                    status="active",
                )
                db.add(connection)
                db.flush()

            existing_cred = db.query(AccountCredential).filter(
                AccountCredential.connection_id == connection.id,
                AccountCredential.credential_type == "plaid_access_token",
            ).first()
            if existing_cred:
                setattr(existing_cred, "value", encrypt_secret(access_token))
            else:
                db.add(
                    AccountCredential(
                        connection_id=connection.id,
                        credential_type="plaid_access_token",
                        value=encrypt_secret(access_token),
                    )
                )

            db.commit()
            db.refresh(connection)
            return [connection]

        raise ValueError("Unsupported provider")

    @staticmethod
    def _load_plaid_cursor(db: Session, connection_id: int) -> str | None:
        row = db.query(AccountCredential).filter(
            AccountCredential.connection_id == connection_id,
            AccountCredential.credential_type == "plaid_transactions_cursor",
        ).first()
        if not row:
            return None
        value = str(getattr(row, "value") or "").strip()
        return value or None

    @staticmethod
    def _store_plaid_cursor(db: Session, connection_id: int, cursor: str) -> None:
        row = db.query(AccountCredential).filter(
            AccountCredential.connection_id == connection_id,
            AccountCredential.credential_type == "plaid_transactions_cursor",
        ).first()
        if row:
            setattr(row, "value", cursor)
            return

        db.add(
            AccountCredential(
                connection_id=connection_id,
                credential_type="plaid_transactions_cursor",
                value=cursor,
            )
        )

    @staticmethod
    def _sync_plaid_transactions(db: Session, user_id: int, connection_id: int, connection: AccountConnection) -> None:
        cursor = SyncService._load_plaid_cursor(db=db, connection_id=connection_id)
        has_more = True
        next_cursor = cursor

        while has_more:
            result = fetch_plaid_transactions_sync(connection=connection, cursor=next_cursor)
            added = result.get("added") if isinstance(result.get("added"), list) else []
            modified = result.get("modified") if isinstance(result.get("modified"), list) else []
            removed = result.get("removed") if isinstance(result.get("removed"), list) else []
            has_more = bool(result.get("has_more"))
            next_cursor_raw = result.get("next_cursor")
            next_cursor = str(next_cursor_raw).strip() if next_cursor_raw is not None else next_cursor

            for item in added + modified:
                if not isinstance(item, dict):
                    continue

                transaction_id = str(item.get("transaction_id") or "").strip()
                if not transaction_id:
                    continue

                category = item.get("personal_finance_category")
                primary = ""
                if isinstance(category, dict):
                    primary = str(category.get("primary") or "")

                row = db.query(PlaidTransaction).filter(
                    PlaidTransaction.account_connection_id == connection_id,
                    PlaidTransaction.transaction_id == transaction_id,
                ).first()

                if row is None:
                    row = PlaidTransaction(
                        user_id=user_id,
                        account_connection_id=connection_id,
                        transaction_id=transaction_id,
                    )
                    db.add(row)

                row.account_id = str(item.get("account_id") or "") or None
                row.date_posted = parse_transaction_date(item.get("date"))
                row.amount = float(item.get("amount") or 0.0)
                row.currency = str(item.get("iso_currency_code") or "USD")
                row.name = str(item.get("name") or "")
                row.merchant_name = str(item.get("merchant_name") or "") or None
                row.category_primary = primary or None
                row.pending = bool(item.get("pending"))
                row.is_removed = False
                row.raw_payload = json.dumps(item)

            for item in removed:
                if not isinstance(item, dict):
                    continue
                transaction_id = str(item.get("transaction_id") or "").strip()
                if not transaction_id:
                    continue
                row = db.query(PlaidTransaction).filter(
                    PlaidTransaction.account_connection_id == connection_id,
                    PlaidTransaction.transaction_id == transaction_id,
                ).first()
                if row:
                    row.is_removed = True

        if next_cursor:
            SyncService._store_plaid_cursor(db=db, connection_id=connection_id, cursor=next_cursor)

    @staticmethod
    def create_sync_job(db: Session, user_id: int, account_id: Optional[int], mode: str = "quick") -> SyncJob:
        sync_mode = (mode or "quick").strip().lower()
        if sync_mode not in {"quick", "deep"}:
            sync_mode = "quick"

        job = SyncJob(
            user_id=user_id,
            account_connection_id=account_id,
            status=SyncJobStatus.PENDING,
            sync_mode=sync_mode,
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def run_sync_job(job_id: int) -> None:
        db = SessionLocal()
        try:
            job = db.query(SyncJob).filter(SyncJob.id == job_id).first()
            if not job:
                return

            setattr(job, "status", SyncJobStatus.IN_PROGRESS)
            setattr(job, "started_at", datetime.utcnow())
            setattr(job, "error_message", None)
            db.commit()

            job_user_id = int(getattr(job, "user_id"))
            selected_account_id = getattr(job, "account_connection_id")

            query = db.query(AccountConnection).filter(
                AccountConnection.user_id == job_user_id,
                AccountConnection.status == "active",
            )
            if selected_account_id is not None:
                query = query.filter(AccountConnection.id == int(selected_account_id))
            connections = query.all()

            new_assets = 0
            updated_assets = 0
            chains_scanned = 0
            tokens_imported = 0
            warnings: List[str] = []
            sync_mode = str(getattr(job, "sync_mode") or "quick")

            for connection in connections:
                provider_value = SyncService._enum_value(getattr(connection, "provider"))
                connection_id = int(getattr(connection, "id"))
                connection_account_type = SyncService._enum_value(getattr(connection, "account_type"))

                if provider_value == AccountProvider.EVM.value:
                    result: EvmHoldingsResult = fetch_evm_holdings(connection, mode=sync_mode)
                    holdings = result.holdings
                    chains_scanned += len(result.scanned_chains)
                    warnings.extend([f"connection:{connection_id}:{item}" for item in result.warnings])
                elif provider_value == AccountProvider.PLAID.value:
                    balance_holdings = fetch_plaid_holdings(connection)
                    try:
                        investment_holdings = fetch_plaid_investment_holdings(connection)
                    except Exception as exc:
                        investment_holdings = []
                        warnings.append(f"connection:{connection_id}:investments_holdings:{str(exc)}")
                    by_id = {item.external_holding_id: item for item in balance_holdings}
                    for inv in investment_holdings:
                        by_id[inv.external_holding_id] = inv
                    holdings = list(by_id.values())

                    try:
                        SyncService._sync_plaid_transactions(
                            db=db,
                            user_id=job_user_id,
                            connection_id=connection_id,
                            connection=connection,
                        )
                    except Exception as exc:
                        warnings.append(f"connection:{connection_id}:transactions_sync:{str(exc)}")
                else:
                    continue

                for item in holdings:
                    ext = db.query(ExternalHolding).filter(
                        ExternalHolding.account_connection_id == connection_id,
                        ExternalHolding.external_holding_id == item.external_holding_id,
                    ).first()

                    if ext:
                        setattr(ext, "amount", item.amount)
                        setattr(ext, "price_usd", item.price_usd)
                        setattr(ext, "value_usd", item.value_usd)
                        setattr(ext, "currency", item.currency)
                        setattr(ext, "raw_payload", serialize_payload(item.raw_payload))
                        existing_asset_id = getattr(ext, "asset_id")
                        if existing_asset_id is not None:
                            linked_asset = db.query(Asset).filter(
                                Asset.user_id == job_user_id,
                                Asset.id == existing_asset_id,
                            ).first()
                            if linked_asset:
                                setattr(linked_asset, "value", item.value_usd)
                                setattr(linked_asset, "currency", item.currency)
                                setattr(linked_asset, "name", item.name)
                                setattr(
                                    linked_asset,
                                    "asset_type",
                                    SyncService._resolve_asset_category(
                                        provider_value,
                                        connection_account_type,
                                        item.raw_payload,
                                    ),
                                )
                        updated_assets += 1
                        tokens_imported += 1
                    else:
                        asset_type = SyncService._resolve_asset_category(
                            provider_value,
                            connection_account_type,
                            item.raw_payload,
                        )
                        asset = Asset(
                            id=get_next_asset_id(db, job_user_id),
                            user_id=job_user_id,
                            name=item.name,
                            asset_type=asset_type,
                            value=item.value_usd,
                            currency=item.currency,
                            category=provider_value,
                            description=f"Synced from {provider_value}",
                        )
                        db.add(asset)
                        db.flush()

                        ext = ExternalHolding(
                            user_id=job_user_id,
                            account_connection_id=connection_id,
                            asset_id=int(getattr(asset, "id")),
                            external_holding_id=item.external_holding_id,
                            symbol=item.symbol,
                            name=item.name,
                            amount=item.amount,
                            price_usd=item.price_usd,
                            value_usd=item.value_usd,
                            currency=item.currency,
                            raw_payload=serialize_payload(item.raw_payload),
                        )
                        db.add(ext)
                        new_assets += 1
                        tokens_imported += 1

                setattr(connection, "last_synced_at", datetime.utcnow())
                setattr(connection, "last_error", None)

            WellnessMetricsService.record_daily_snapshot(db=db, user_id=job_user_id, source="sync")

            setattr(job, "status", SyncJobStatus.SUCCESS)
            setattr(job, "completed_at", datetime.utcnow())
            setattr(job, "new_assets_count", new_assets)
            setattr(job, "updated_assets_count", updated_assets)
            setattr(job, "chains_scanned", chains_scanned)
            setattr(job, "tokens_imported", tokens_imported)
            setattr(job, "warnings_json", serialize_payload({"warnings": warnings}))
            db.commit()

        except (ProviderError, ValueError) as exc:
            db.rollback()
            job = db.query(SyncJob).filter(SyncJob.id == job_id).first()
            if job:
                setattr(job, "status", SyncJobStatus.FAILED)
                setattr(job, "error_message", str(exc))
                setattr(job, "completed_at", datetime.utcnow())
                setattr(job, "chains_scanned", 0)
                setattr(job, "tokens_imported", 0)
                setattr(job, "warnings_json", serialize_payload({"warnings": []}))
                db.commit()
        except Exception as exc:
            db.rollback()
            job = db.query(SyncJob).filter(SyncJob.id == job_id).first()
            if job:
                setattr(job, "status", SyncJobStatus.FAILED)
                setattr(job, "error_message", f"Unexpected sync error: {str(exc)}")
                setattr(job, "completed_at", datetime.utcnow())
                setattr(job, "chains_scanned", 0)
                setattr(job, "tokens_imported", 0)
                setattr(job, "warnings_json", serialize_payload({"warnings": []}))
                db.commit()
        finally:
            db.close()
