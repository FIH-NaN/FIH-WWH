from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from src.server.services.auth.security import get_current_user

from src.server.db.database import get_db
from src.server.db.tables.transaction import Transaction
from src.server.db.tables.assets import Asset
from src.server.db.tables.user import User

from src.server.routers.web_view_model.schemas import (
    TransactionCreate,
    TransactionResponse,
    TransactionImportRequest,
    SuccessResponse,
)

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("", response_model=SuccessResponse)
def list_transactions(
    asset_id: Optional[int] = Query(None),
    transaction_type: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get list of transactions."""
    query = db.query(Transaction).filter(Transaction.user_id == user.id)

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
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new transaction."""
    # Verify asset exists and belongs to user
    asset = db.query(Asset).filter(
        Asset.id == transaction.asset_id, Asset.user_id == user.id
    ).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )

    new_transaction = Transaction(
        user_id=user.id,
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
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Batch import transactions."""
    imported = []
    failed = []

    for item in request.transactions:
        try:
            # Verify asset exists and belongs to user
            asset = db.query(Asset).filter(
                Asset.id == item.asset_id, Asset.user_id == user.id
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
                user_id=user.id,
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
