from fastapi import APIRouter, Depends, Header, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from database import get_db
from models import Transaction, Asset, User
from schemas import (
    TransactionCreate,
    TransactionResponse,
    TransactionImportRequest,
    SuccessResponse,
)
from core.security import decode_access_token

router = APIRouter(prefix="/transactions", tags=["transactions"])


def get_current_user(token: str = None, db: Session = Depends(get_db)) -> User:
    """Dependency to get current user from token."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    user_id = decode_access_token(token)
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


def get_current_user_from_auth(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db),
) -> User:
    resolved_token = token
    if authorization:
        resolved_token = authorization.split(" ", 1)[1] if authorization.startswith("Bearer ") else authorization
    return get_current_user(resolved_token, db)


@router.get("", response_model=SuccessResponse)
def list_transactions(
    asset_id: Optional[int] = Query(None),
    transaction_type: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user_from_auth),
    db: Session = Depends(get_db),
):
    """Get list of transactions."""
    query = db.query(Transaction).filter(Transaction.user_id == current_user.id)

    if asset_id:
        query = query.filter(Transaction.asset_id == asset_id)
    if transaction_type:
        query = query.filter(Transaction.transaction_type == transaction_type)
    if start_date:
        query = query.filter(Transaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(Transaction.transaction_date <= end_date)

    transactions = query.order_by(Transaction.transaction_date.desc()).all()

    return SuccessResponse(
        success=True,
        data={
            "transactions": [
                TransactionResponse.model_validate(t).model_dump() for t in transactions
            ]
        },
    )


@router.post("", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction: TransactionCreate,
    current_user: User = Depends(get_current_user_from_auth),
    db: Session = Depends(get_db),
):
    """Create a new transaction."""
    # Verify asset exists and belongs to user
    asset = db.query(Asset).filter(
        Asset.id == transaction.asset_id, Asset.user_id == current_user.id
    ).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )

    new_transaction = Transaction(
        user_id=current_user.id,
        asset_id=transaction.asset_id,
        transaction_type=transaction.transaction_type,
        amount=transaction.amount,
        category=transaction.category,
        description=transaction.description,
        transaction_date=transaction.transaction_date or datetime.utcnow(),
    )
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return SuccessResponse(
        success=True,
        data=TransactionResponse.model_validate(new_transaction).model_dump(),
    )


@router.post("/import", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
def import_transactions(
    request: TransactionImportRequest,
    current_user: User = Depends(get_current_user_from_auth),
    db: Session = Depends(get_db),
):
    """Batch import transactions."""
    imported = []
    failed = []

    for item in request.transactions:
        try:
            # Verify asset exists and belongs to user
            asset = db.query(Asset).filter(
                Asset.id == item.asset_id, Asset.user_id == current_user.id
            ).first()
            if not asset:
                failed.append(
                    {
                        "asset_id": item.asset_id,
                        "error": "Asset not found",
                    }
                )
                continue

            new_transaction = Transaction(
                user_id=current_user.id,
                asset_id=item.asset_id,
                transaction_type=item.transaction_type,
                amount=item.amount,
                category=item.category,
                transaction_date=item.transaction_date or datetime.utcnow(),
            )
            db.add(new_transaction)
            imported.append(item.asset_id)
        except Exception as e:
            failed.append(
                {
                    "asset_id": item.asset_id,
                    "error": str(e),
                }
            )

    db.commit()

    return SuccessResponse(
        success=True,
        data={
            "imported_count": len(imported),
            "failed_count": len(failed),
            "failed": failed,
        },
    )
