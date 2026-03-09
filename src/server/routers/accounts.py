import json
from collections import defaultdict

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.server.db.database import get_db
from src.server.db.tables.assets import Asset
from src.server.db.tables.user import User
from src.server.db.tables.wallet import AccountConnection, AccountProvider, ExternalHolding, SyncJob
from src.server.routers.web_view_model.schemas import (
    AccountConnectRequest,
    PlaidLinkTokenResponse,
    AccountSyncRequest,
    AccountSyncStatusResponse,
    AccountSyncTriggerResponse,
    SuccessResponse,
    WalletChainGroup,
    WalletHoldingItem,
    WalletHoldingsPayload,
    WalletSummaryItem,
    WalletSummaryPayload,
)
from src.server.services.auth.security import get_current_user
from src.server.services.wallet_sync.constants import MIN_VISIBLE_TOKEN_USD
from src.server.services.wallet_sync.providers import create_plaid_link_token
from src.server.services.wallet_sync.sync_service import SyncService


router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("/connect", response_model=SuccessResponse)
def connect_account(
    payload: AccountConnectRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    provider = payload.provider.lower().strip()

    if provider not in {AccountProvider.EVM.value, AccountProvider.PLAID.value}:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Provider not supported in current release",
        )

    try:
        connections = SyncService.connect_account(
            db=db,
            user=user,
            provider=provider,
            account_type=payload.type,
            credentials=payload.credentials,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Provider error: {str(exc)}") from exc

    data = []
    for c in connections:
        provider_value = c.provider.value if hasattr(c.provider, "value") else str(c.provider)
        account_type_value = c.account_type.value if hasattr(c.account_type, "value") else str(c.account_type)
        data.append(
            {
                "id": c.id,
                "type": account_type_value,
                "provider": provider_value,
                "name": c.name,
                "network": c.network,
                "wallet_address": c.wallet_address,
                "last_synced": c.last_synced_at,
                "status": c.status,
            }
        )

    return SuccessResponse(success=True, data={"accounts": data})


@router.get("/plaid/link-token", response_model=SuccessResponse)
def get_plaid_link_token(user: User = Depends(get_current_user)):
    try:
        payload = create_plaid_link_token(user_id=int(getattr(user, "id")))
        result = PlaidLinkTokenResponse(
            link_token=str(payload.get("link_token") or ""),
            expiration=payload.get("expiration"),
            request_id=payload.get("request_id"),
        )
        if not result.link_token:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Failed to create Plaid link token")
        return SuccessResponse(success=True, data=result.model_dump())
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Plaid link token error: {str(exc)}") from exc


@router.get("", response_model=SuccessResponse)
def list_accounts(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = db.query(AccountConnection).filter(AccountConnection.user_id == user.id).order_by(AccountConnection.created_at.desc()).all()

    data = []
    for row in rows:
        provider_value = row.provider.value if hasattr(row.provider, "value") else str(row.provider)
        account_type_value = row.account_type.value if hasattr(row.account_type, "value") else str(row.account_type)
        data.append(
            {
                "id": row.id,
                "type": account_type_value,
                "provider": provider_value,
                "name": row.name,
                "network": row.network,
                "wallet_address": row.wallet_address,
                "last_synced": row.last_synced_at,
                "status": row.status,
                "last_error": row.last_error,
            }
        )

    return SuccessResponse(success=True, data={"accounts": data})


@router.delete("", response_model=SuccessResponse)
def delete_account(
    id: int = Query(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    row = db.query(AccountConnection).filter(AccountConnection.id == id, AccountConnection.user_id == user.id).first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    holdings = db.query(ExternalHolding).filter(
        ExternalHolding.user_id == user.id,
        ExternalHolding.account_connection_id == id,
    ).all()

    asset_ids = {int(getattr(item, "asset_id")) for item in holdings if getattr(item, "asset_id") is not None}
    removed_assets = 0

    for asset_id in asset_ids:
        shared_ref = db.query(ExternalHolding.id).filter(
            ExternalHolding.user_id == user.id,
            ExternalHolding.asset_id == asset_id,
            ExternalHolding.account_connection_id != id,
        ).first()
        if shared_ref is not None:
            continue

        removed_assets += db.query(Asset).filter(
            Asset.id == asset_id,
            Asset.user_id == user.id,
        ).delete(synchronize_session=False)

    db.query(ExternalHolding).filter(
        ExternalHolding.user_id == user.id,
        ExternalHolding.account_connection_id == id,
    ).delete(synchronize_session=False)

    db.delete(row)
    db.commit()
    return SuccessResponse(success=True, message=f"Account disconnected. Removed {removed_assets} synced assets.")


@router.post("/sync", response_model=SuccessResponse)
def sync_accounts(
    payload: AccountSyncRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.account_id is not None:
        target = db.query(AccountConnection).filter(
            AccountConnection.id == payload.account_id,
            AccountConnection.user_id == user.id,
            AccountConnection.status == "active",
        ).first()
        if not target:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    user_id = getattr(user, "id")
    sync_mode = (payload.mode or "quick").strip().lower()
    if sync_mode not in {"quick", "deep"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="mode must be quick or deep")

    job = SyncService.create_sync_job(db=db, user_id=int(user_id), account_id=payload.account_id, mode=sync_mode)
    job_id = int(getattr(job, "id"))
    background_tasks.add_task(SyncService.run_sync_job, job_id)

    job_status = getattr(job, "status")
    result = AccountSyncTriggerResponse(job_id=job_id, status=job_status.value if hasattr(job_status, "value") else str(job_status))
    return SuccessResponse(success=True, data=result.model_dump())


@router.get("/sync/{job_id}", response_model=SuccessResponse)
def get_sync_status(
    job_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = db.query(SyncJob).filter(SyncJob.id == job_id, SyncJob.user_id == user.id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sync job not found")

    job_status = getattr(job, "status")
    status_value = job_status.value if hasattr(job_status, "value") else str(job_status)
    sync_mode = str(getattr(job, "sync_mode") or "quick")
    raw_chains_scanned = getattr(job, "chains_scanned") or 0
    chains_scanned = int(raw_chains_scanned) if isinstance(raw_chains_scanned, (int, float, str)) else 0
    raw_tokens_imported = getattr(job, "tokens_imported") or 0
    tokens_imported = int(raw_tokens_imported) if isinstance(raw_tokens_imported, (int, float, str)) else 0
    warnings_json = getattr(job, "warnings_json")
    warnings_obj = _parse_holding_payload(warnings_json)
    raw_warnings = warnings_obj.get("warnings", []) if isinstance(warnings_obj, dict) else []
    warnings = [str(item) for item in raw_warnings] if isinstance(raw_warnings, list) else []
    payload = AccountSyncStatusResponse(
        job_id=int(getattr(job, "id")),
        status=status_value,
        sync_mode=sync_mode,
        started_at=getattr(job, "started_at"),
        completed_at=getattr(job, "completed_at"),
        new_assets_count=int(getattr(job, "new_assets_count") or 0),
        updated_assets_count=int(getattr(job, "updated_assets_count") or 0),
        chains_scanned=chains_scanned,
        tokens_imported=tokens_imported,
        warnings=warnings,
        error_message=getattr(job, "error_message"),
    )

    return SuccessResponse(success=True, data=payload.model_dump())


def _parse_holding_payload(raw_payload: object) -> dict:
    if isinstance(raw_payload, str):
        try:
            data = json.loads(raw_payload)
            return data if isinstance(data, dict) else {}
        except (TypeError, ValueError):
            return {}
    if isinstance(raw_payload, dict):
        return raw_payload
    return {}


@router.get("/wallets/summary", response_model=SuccessResponse)
def wallet_summary(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = db.query(AccountConnection).filter(
        AccountConnection.user_id == user.id,
    ).order_by(AccountConnection.last_synced_at.desc(), AccountConnection.created_at.desc()).all()

    wallet_items: list[WalletSummaryItem] = []
    total_portfolio = 0.0
    for row in rows:
        provider_value = row.provider.value if hasattr(row.provider, "value") else str(row.provider)
        holdings = db.query(ExternalHolding).filter(
            ExternalHolding.user_id == user.id,
            ExternalHolding.account_connection_id == row.id,
            ExternalHolding.value_usd >= MIN_VISIBLE_TOKEN_USD,
        ).all()

        total_value_usd = sum(float(getattr(item, "value_usd") or 0.0) for item in holdings)
        chain_keys = set()
        for item in holdings:
            if provider_value != AccountProvider.EVM.value:
                continue
            payload = _parse_holding_payload(getattr(item, "raw_payload"))
            chain_data = payload.get("chain", {}) if isinstance(payload.get("chain"), dict) else {}
            chain_name = str(chain_data.get("chain_name") or "unknown")
            chain_id = chain_data.get("chain_id")
            chain_keys.add((chain_name, chain_id))

        total_portfolio += total_value_usd
        provider_attr = getattr(row, "provider")
        account_type_attr = getattr(row, "account_type")
        provider_value = provider_attr.value if hasattr(provider_attr, "value") else str(provider_attr)
        account_type_value = account_type_attr.value if hasattr(account_type_attr, "value") else str(account_type_attr)
        account_id = int(getattr(row, "id"))
        wallet_address = getattr(row, "wallet_address")
        network = getattr(row, "network")
        last_synced = getattr(row, "last_synced_at")
        status_value = str(getattr(row, "status"))
        last_error = getattr(row, "last_error")
        wallet_items.append(
            WalletSummaryItem(
                account_id=account_id,
                name=str(row.name),
                provider=provider_value,
                type=account_type_value,
                wallet_address=str(wallet_address) if wallet_address else None,
                network=str(network) if network else None,
                total_value_usd=total_value_usd,
                token_count=len(holdings),
                active_chain_count=len(chain_keys),
                last_synced=last_synced,
                status=status_value,
                last_error=str(last_error) if last_error else None,
            )
        )

    payload = WalletSummaryPayload(wallets=wallet_items, total_portfolio_usd=total_portfolio)
    return SuccessResponse(success=True, data=payload.model_dump())


@router.get("/wallets/{account_id}/holdings", response_model=SuccessResponse)
def wallet_holdings(
    account_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    connection = db.query(AccountConnection).filter(
        AccountConnection.id == account_id,
        AccountConnection.user_id == user.id,
    ).first()
    if not connection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet account not found")

    connection_provider = getattr(connection, "provider")
    is_plaid = connection_provider == AccountProvider.PLAID

    holdings = db.query(ExternalHolding).filter(
        ExternalHolding.user_id == user.id,
        ExternalHolding.account_connection_id == account_id,
        ExternalHolding.value_usd >= MIN_VISIBLE_TOKEN_USD,
    ).order_by(ExternalHolding.value_usd.desc()).all()

    groups: dict[tuple[str, int | None], list[WalletHoldingItem]] = defaultdict(list)
    subtotals: dict[tuple[str, int | None], float] = defaultdict(float)
    total = 0.0

    for row in holdings:
        payload = _parse_holding_payload(getattr(row, "raw_payload"))
        if is_plaid:
            account_data = payload.get("account", {}) if isinstance(payload.get("account"), dict) else payload
            plaid_type = str(account_data.get("type") or "account")
            plaid_subtype = str(account_data.get("subtype") or "").strip()
            group_suffix = plaid_subtype.title() if plaid_subtype else plaid_type.title()
            chain_name = f"Plaid {group_suffix}"
            chain_id = None
            token_data = account_data
        else:
            chain_data = payload.get("chain", {}) if isinstance(payload.get("chain"), dict) else {}
            chain_name = str(chain_data.get("chain_name") or "unknown")
            chain_id_raw = chain_data.get("chain_id")
            try:
                chain_id = int(chain_id_raw) if chain_id_raw is not None else None
            except (TypeError, ValueError):
                chain_id = None

            token_data = payload.get("token", {}) if isinstance(payload.get("token"), dict) else {}

        logo_urls_obj = token_data.get("logo_urls")
        logo_urls = logo_urls_obj if isinstance(logo_urls_obj, dict) else {}
        logo_url = str(
            logo_urls.get("token_logo_url")
            or token_data.get("logo_url")
            or ""
        ) or None

        value_usd = float(getattr(row, "value_usd") or 0.0)
        item = WalletHoldingItem(
            external_holding_id=str(getattr(row, "external_holding_id") or ""),
            name=str(getattr(row, "name") or ""),
            symbol=str(getattr(row, "symbol") or ""),
            amount=float(getattr(row, "amount") or 0.0),
            value_usd=value_usd,
            price_usd=float(getattr(row, "price_usd") or 0.0),
            chain_name=chain_name,
            chain_id=chain_id,
            logo_url=logo_url,
        )

        key = (chain_name, chain_id)
        groups[key].append(item)
        subtotals[key] += value_usd
        total += value_usd

    chain_groups: list[WalletChainGroup] = []
    for key, tokens in groups.items():
        chain_name, chain_id = key
        sorted_tokens = sorted(tokens, key=lambda token: token.value_usd, reverse=True)
        chain_groups.append(
            WalletChainGroup(
                chain_name=chain_name,
                chain_id=chain_id,
                subtotal_usd=float(subtotals[key]),
                tokens=sorted_tokens,
            )
        )

    chain_groups.sort(key=lambda group: group.subtotal_usd, reverse=True)
    payload = WalletHoldingsPayload(
        account_id=account_id,
        wallet_address=str(getattr(connection, "wallet_address") or "") or None,
        total_value_usd=total,
        chains=chain_groups,
    )
    return SuccessResponse(success=True, data=payload.model_dump())
