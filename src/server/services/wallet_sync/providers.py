import json
import logging
import re
from dataclasses import dataclass
from typing import List, Optional, Set
from urllib import parse, request

from sqlalchemy.orm import Session

from src.server.config import get_settings
from src.server.core.secrets import decrypt_secret
from src.server.db.tables.wallet import AccountConnection, AccountCredential


logger = logging.getLogger(__name__)


EVM_ADDRESS_PATTERN = re.compile(r"^0x[a-fA-F0-9]{40}$")

CHAIN_ID_TO_NAME = {
    1: "eth-mainnet",
    10: "optimism-mainnet",
    137: "polygon-mainnet",
    8453: "base-mainnet",
    42161: "arbitrum-mainnet",
}

NETWORK_TO_CHAIN_NAME = {
    "ethereum": "eth-mainnet",
    "optimism": "optimism-mainnet",
    "polygon": "polygon-mainnet",
    "base": "base-mainnet",
    "arbitrum": "arbitrum-mainnet",
}

DEEP_SCAN_CHAIN_NAMES = [
    "eth-mainnet",
    "base-mainnet",
    "polygon-mainnet",
    "arbitrum-mainnet",
    "optimism-mainnet",
]


@dataclass
class HoldingRecord:
    external_holding_id: str
    name: str
    symbol: str
    amount: float
    price_usd: float
    value_usd: float
    currency: str = "USD"
    chain_name: Optional[str] = None
    chain_id: Optional[int] = None
    is_spam: bool = False
    logo_url: Optional[str] = None
    last_transferred_at: Optional[str] = None
    updated_at: Optional[str] = None
    raw_payload: Optional[dict] = None


class ProviderError(Exception):
    """Provider-side failure while fetching account balances."""


@dataclass
class ActivityRecord:
    chain_name: str
    chain_id: str
    first_seen_at: Optional[str]
    last_seen_at: Optional[str]


@dataclass
class EvmHoldingsResult:
    holdings: List[HoldingRecord]
    scanned_chains: List[str]
    failed_chains: List[str]
    warnings: List[str]
    used_mode: str


def _http_post_json(url: str, payload: dict, timeout: int = 10) -> dict:
    encoded = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        data=encoded,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body) if body else {}


def _http_get_json(url: str, params: Optional[dict] = None, timeout: int = 10, headers: Optional[dict] = None) -> dict:
    final_url = url
    if params:
        final_url = f"{url}?{parse.urlencode(params)}"
    req = request.Request(final_url, headers=headers or {}, method="GET")
    with request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body) if body else {}


def _goldrush_headers() -> dict:
    settings = get_settings()
    if not settings.GOLDRUSH_API_KEY:
        raise ProviderError("Missing GOLDRUSH_API_KEY for Foundational API calls")
    return {
        "Authorization": f"Bearer {settings.GOLDRUSH_API_KEY}",
        "Accept": "application/json",
        "User-Agent": "WWH-GoldRush-Client/1.0",
    }


def _get_credential(connection: AccountConnection, key: str) -> Optional[str]:
    for item in connection.credentials:
        if item.credential_type == key:
            if key == "plaid_access_token":
                return decrypt_secret(item.value)
            return item.value
    return None


def _upsert_credential(db: Session, connection: AccountConnection, key: str, value: str) -> None:
    existing = db.query(AccountCredential).filter(
        AccountCredential.connection_id == connection.id,
        AccountCredential.credential_type == key,
    ).first()

    if existing:
        setattr(existing, "value", value)
    else:
        db.add(
            AccountCredential(
                connection_id=connection.id,
                credential_type=key,
                value=value,
            )
        )


def validate_evm_address(address: str) -> bool:
    return bool(EVM_ADDRESS_PATTERN.match(address))


def _parse_float(value: object) -> float:
    try:
        return float(str(value or 0.0))
    except (TypeError, ValueError):
        return 0.0


def _parse_amount(raw_balance: object, decimals: object) -> float:
    raw = str(raw_balance or "0")
    try:
        decimal_places = int(str(decimals or 0))
    except (TypeError, ValueError):
        decimal_places = 0

    try:
        return float(int(raw) / (10 ** max(decimal_places, 0)))
    except (TypeError, ValueError, OverflowError):
        return 0.0


def _normalize_chain_name(chain_name: str) -> str:
    lowered = (chain_name or "").strip().lower()
    if lowered in NETWORK_TO_CHAIN_NAME:
        return NETWORK_TO_CHAIN_NAME[lowered]
    return lowered


def _extract_data_payload(payload: dict) -> dict:
    data = payload.get("data")
    if isinstance(data, dict):
        return data
    return payload


def _derive_target_chains(connection: AccountConnection, mode: str, activity: List[ActivityRecord]) -> List[str]:
    chains: Set[str] = set()

    network_fallback = _normalize_chain_name(str(getattr(connection, "network", "") or "ethereum"))
    normalized_network_chain = NETWORK_TO_CHAIN_NAME.get(network_fallback, network_fallback)
    if normalized_network_chain:
        chains.add(normalized_network_chain)

    for item in activity:
        try:
            mapped = CHAIN_ID_TO_NAME.get(int(item.chain_id))
        except (TypeError, ValueError):
            mapped = None

        if mapped:
            chains.add(mapped)
            continue

        normalized = _normalize_chain_name(item.chain_name)
        if normalized:
            chains.add(normalized)

    if mode == "deep":
        chains.update(DEEP_SCAN_CHAIN_NAMES)

    if not chains:
        chain = NETWORK_TO_CHAIN_NAME.get(network_fallback, network_fallback)
        chains.add(chain if chain else "eth-mainnet")

    return sorted(chains)


def _fetch_balances_v2(wallet_address: str, chain_name: str) -> dict:
    payload = _http_get_json(
        f"https://api.covalenthq.com/v1/{chain_name}/address/{wallet_address}/balances_v2/",
        params={
            "quote-currency": "USD",
            "no-spam": "true",
        },
        headers=_goldrush_headers(),
        timeout=12,
    )
    return _extract_data_payload(payload)


def fetch_evm_holdings(connection: AccountConnection, mode: str = "quick") -> EvmHoldingsResult:
    wallet_address = (connection.wallet_address or connection.provider_account_id or "").lower()
    if not wallet_address:
        raise ProviderError("Missing wallet address for EVM connection")

    sync_mode = (mode or "quick").strip().lower()
    if sync_mode not in {"quick", "deep"}:
        sync_mode = "quick"

    activity: List[ActivityRecord] = []
    warnings: List[str] = []
    try:
        activity = fetch_address_activity(wallet_address, include_testnets=False)
    except Exception as exc:
        warnings.append(f"activity:{str(exc)}")

    target_chains = _derive_target_chains(connection, sync_mode, activity)
    scanned_chains: List[str] = []
    failed_chains: List[str] = []
    holdings: List[HoldingRecord] = []

    for chain_name in target_chains:
        try:
            data = _fetch_balances_v2(wallet_address=wallet_address, chain_name=chain_name)
            scanned_chains.append(chain_name)
            chain_id_raw = data.get("chain_id")
            try:
                chain_id = int(chain_id_raw) if chain_id_raw is not None else None
            except (TypeError, ValueError):
                chain_id = None

            updated_at = str(data.get("updated_at") or "") or None
            items = data.get("items") or []
            if not isinstance(items, list):
                continue

            for item in items:
                if not isinstance(item, dict):
                    continue
                if bool(item.get("is_spam")):
                    continue

                amount = _parse_amount(item.get("balance"), item.get("contract_decimals"))
                quote = _parse_float(item.get("quote"))
                price_usd = _parse_float(item.get("quote_rate"))
                if amount <= 0 and quote <= 0:
                    continue

                symbol = str(item.get("contract_ticker_symbol") or "TOKEN")
                contract_address = str(item.get("contract_address") or "").lower()
                holding_id = contract_address or symbol.lower()
                resolved_chain_name = str(data.get("chain_name") or chain_name)
                logo_urls_obj = item.get("logo_urls")
                logo_urls = logo_urls_obj if isinstance(logo_urls_obj, dict) else {}
                logo_url = str(
                    logo_urls.get("token_logo_url")
                    or item.get("logo_url")
                    or ""
                ) or None

                holdings.append(
                    HoldingRecord(
                        external_holding_id=f"{resolved_chain_name}:token:{holding_id}",
                        name=str(item.get("contract_display_name") or item.get("contract_name") or symbol),
                        symbol=symbol,
                        amount=amount,
                        price_usd=price_usd,
                        value_usd=quote if quote > 0 else amount * price_usd,
                        currency="USD",
                        chain_name=resolved_chain_name,
                        chain_id=chain_id,
                        is_spam=bool(item.get("is_spam")),
                        logo_url=logo_url,
                        last_transferred_at=str(item.get("last_transferred_at") or "") or None,
                        updated_at=updated_at,
                        raw_payload={
                            "chain": {
                                "chain_id": chain_id,
                                "chain_name": resolved_chain_name,
                                "updated_at": updated_at,
                            },
                            "token": item,
                        },
                    )
                )
        except Exception as exc:
            failed_chains.append(chain_name)
            warnings.append(f"balances_v2:{chain_name}:{str(exc)}")
            logger.warning("balances_v2 fetch failed for %s on %s: %s", wallet_address, chain_name, exc)

    if not scanned_chains:
        raise ProviderError("Unable to fetch balances_v2 on any target chain")

    return EvmHoldingsResult(
        holdings=holdings,
        scanned_chains=scanned_chains,
        failed_chains=failed_chains,
        warnings=warnings,
        used_mode=sync_mode,
    )


def fetch_address_activity(wallet_address: str, include_testnets: bool = False) -> List[ActivityRecord]:
    payload = _http_get_json(
        f"https://api.covalenthq.com/v1/address/{wallet_address}/activity/",
        params={"testnets": "true" if include_testnets else "false"},
        headers=_goldrush_headers(),
        timeout=12,
    )

    items = payload.get("items") or payload.get("data", {}).get("items", [])
    results: List[ActivityRecord] = []
    for item in items:
        meta = item.get("extends", {})
        results.append(
            ActivityRecord(
                chain_name=_normalize_chain_name(str(meta.get("name") or "")),
                chain_id=str(meta.get("chain_id") or ""),
                first_seen_at=item.get("first_seen_at"),
                last_seen_at=item.get("last_seen_at"),
            )
        )
    return results


def exchange_plaid_public_token(public_token: str) -> dict:
    settings = get_settings()
    env = settings.PLAID_ENV or "sandbox"
    base_url = f"https://{env}.plaid.com"
    resp = _http_post_json(
        f"{base_url}/item/public_token/exchange",
        {
            "client_id": settings.PLAID_CLIENT_ID,
            "secret": settings.PLAID_SECRET,
            "public_token": public_token,
        },
        timeout=10,
    )
    return resp


def fetch_plaid_holdings(connection: AccountConnection) -> List[HoldingRecord]:
    settings = get_settings()
    access_token = _get_credential(connection, "plaid_access_token")
    if not access_token:
        raise ProviderError("Missing Plaid access token for this connection")

    env = settings.PLAID_ENV or "sandbox"
    base_url = f"https://{env}.plaid.com"
    data = _http_post_json(
        f"{base_url}/accounts/balance/get",
        {
            "client_id": settings.PLAID_CLIENT_ID,
            "secret": settings.PLAID_SECRET,
            "access_token": access_token,
        },
        timeout=10,
    )

    holdings: List[HoldingRecord] = []
    for account in data.get("accounts", []):
        balances = account.get("balances", {})
        current_balance = float(balances.get("current") or 0.0)
        iso_currency = balances.get("iso_currency_code") or "USD"
        account_id = account.get("account_id")
        account_name = account.get("name") or "Plaid Account"

        holdings.append(
            HoldingRecord(
                external_holding_id=f"plaid:account:{account_id}",
                name=account_name,
                symbol=iso_currency,
                amount=current_balance,
                price_usd=1.0,
                value_usd=current_balance,
                currency=iso_currency,
                raw_payload=account,
            )
        )

    return holdings


def serialize_payload(payload: Optional[dict]) -> str:
    if payload is None:
        return "{}"
    try:
        return json.dumps(payload)
    except TypeError:
        return "{}"
