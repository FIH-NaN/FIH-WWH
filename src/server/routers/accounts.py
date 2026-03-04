from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.security import decode_access_token
from database import get_db
from models import Asset, AssetType, ConnectedAccount, User
from schemas import (
    AccountConnectRequest,
    ConnectedAccountResponse,
    SuccessResponse,
    SyncRequest,
)

router = APIRouter(prefix="/accounts", tags=["accounts"])


def _resolve_token(
    authorization: Optional[str],
    token: Optional[str],
) -> Optional[str]:
    """Resolve token from Bearer header first, then query fallback."""
    if authorization:
        if authorization.startswith("Bearer "):
            return authorization.split(" ", 1)[1]
        return authorization
    return token


def get_current_user(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db),
) -> User:
    resolved_token = _resolve_token(authorization, token)
    if not resolved_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    user_id = decode_access_token(resolved_token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.get("", response_model=SuccessResponse)
def list_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    accounts = (
        db.query(ConnectedAccount)
        .filter(ConnectedAccount.user_id == current_user.id)
        .all()
    )
    return SuccessResponse(
        success=True,
        data=[ConnectedAccountResponse.model_validate(a).model_dump() for a in accounts],
    )


@router.post("/connect", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
def connect_account(
    request: AccountConnectRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account = ConnectedAccount(
        user_id=current_user.id,
        account_type=request.account_type.value,
        provider=request.provider.value,
        name=request.name,
        wallet_address=request.wallet_address,
        network=request.network.value if request.network else None,
        status="active",
    )
    db.add(account)
    db.commit()
    db.refresh(account)

    # Mock assets for non-crypto accounts.
    if request.account_type.value in ["bank", "brokerage"]:
        mock_assets = [
            {
                "name": f"{request.name} - Savings",
                "asset_type": AssetType.CASH,
                "value": 10000,
                "category": "Connected",
            },
            {
                "name": f"{request.name} - Investment",
                "asset_type": AssetType.STOCK,
                "value": 25000,
                "category": "Connected",
            },
        ]
        for asset_data in mock_assets:
            db.add(
                Asset(
                    user_id=current_user.id,
                    name=asset_data["name"],
                    asset_type=asset_data["asset_type"],
                    value=asset_data["value"],
                    category=asset_data["category"],
                    currency="USD",
                )
            )
        db.commit()

    return SuccessResponse(
        success=True,
        data=ConnectedAccountResponse.model_validate(account).model_dump(),
    )


@router.delete("", response_model=SuccessResponse)
def delete_account(
    id: int = Query(..., description="Account ID to delete"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account = (
        db.query(ConnectedAccount)
        .filter(
            ConnectedAccount.id == id,
            ConnectedAccount.user_id == current_user.id,
        )
        .first()
    )

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )

    db.delete(account)
    db.commit()

    return SuccessResponse(success=True, message="Account disconnected")


@router.post("/sync", response_model=SuccessResponse)
def sync_account(
    request: SyncRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account = (
        db.query(ConnectedAccount)
        .filter(
            ConnectedAccount.id == request.account_id,
            ConnectedAccount.user_id == current_user.id,
        )
        .first()
    )

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )

    account.last_synced = datetime.utcnow()
    db.commit()

    return SuccessResponse(
        success=True,
        data={"message": "Sync completed", "synced_at": account.last_synced},
    )
