from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.dependencies import get_current_user
from database import get_db
from models import ConnectedAccount, User
from services.account_service import (
    create_mock_assets_for_connected_account,
    sync_account_and_build_recommendations,
)
from schemas import (
    AccountConnectRequest,
    ConnectedAccountResponse,
    SuccessResponse,
    SyncRequest,
)

router = APIRouter(prefix="/accounts", tags=["accounts"])


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

    create_mock_assets_for_connected_account(
        db=db,
        user_id=current_user.id,
        account_name=request.name,
        account_type=request.account_type.value,
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

    sync_data = sync_account_and_build_recommendations(db, account)

    return SuccessResponse(
        success=True,
        data=sync_data,
    )
