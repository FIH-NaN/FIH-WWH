from fastapi import APIRouter, Depends, Header, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from database import get_db
from models import Asset, User, Transaction
from schemas import (
    AssetCreate,
    AssetResponse,
    AssetUpdate,
    AssetSummary,
    HealthScore,
    HealthScoreFactor,
    SuccessResponse,
)
from core.security import decode_access_token

router = APIRouter(prefix="/assets", tags=["assets"])


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
def list_assets(
    asset_type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user_from_auth),
    db: Session = Depends(get_db),
):
    """Get list of assets."""
    query = db.query(Asset).filter(Asset.user_id == current_user.id)

    if asset_type:
        query = query.filter(Asset.asset_type == asset_type)
    if category:
        query = query.filter(Asset.category == category)

    total = query.count()
    assets = query.offset((page - 1) * limit).limit(limit).all()

    return SuccessResponse(
        success=True,
        data={
            "assets": [AssetResponse.model_validate(a).model_dump() for a in assets],
            "total": total,
            "page": page,
            "limit": limit,
        },
    )


@router.post("", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
def create_asset(
    asset: AssetCreate,
    current_user: User = Depends(get_current_user_from_auth),
    db: Session = Depends(get_db),
):
    """Create a new asset."""
    new_asset = Asset(
        user_id=current_user.id,
        name=asset.name,
        asset_type=asset.asset_type,
        value=asset.value,
        currency=asset.currency,
        category=asset.category,
        description=asset.description,
    )
    db.add(new_asset)
    db.commit()
    db.refresh(new_asset)

    return SuccessResponse(
        success=True,
        data=AssetResponse.model_validate(new_asset).model_dump(),
    )


@router.get("/{asset_id:int}", response_model=SuccessResponse)
def get_asset(
    asset_id: int,
    current_user: User = Depends(get_current_user_from_auth),
    db: Session = Depends(get_db),
):
    """Get single asset by ID."""
    asset = db.query(Asset).filter(
        Asset.id == asset_id, Asset.user_id == current_user.id
    ).first()

    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )

    return SuccessResponse(
        success=True,
        data=AssetResponse.model_validate(asset).model_dump(),
    )


@router.put("/{asset_id:int}", response_model=SuccessResponse)
def update_asset(
    asset_id: int,
    asset: AssetUpdate,
    current_user: User = Depends(get_current_user_from_auth),
    db: Session = Depends(get_db),
):
    """Update asset."""
    db_asset = db.query(Asset).filter(
        Asset.id == asset_id, Asset.user_id == current_user.id
    ).first()

    if not db_asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )

    if asset.name:
        db_asset.name = asset.name
    if asset.value is not None:
        db_asset.value = asset.value
    if asset.description:
        db_asset.description = asset.description

    db.commit()
    db.refresh(db_asset)

    return SuccessResponse(
        success=True,
        data=AssetResponse.model_validate(db_asset).model_dump(),
    )


@router.delete("/{asset_id:int}", response_model=SuccessResponse)
def delete_asset(
    asset_id: int,
    current_user: User = Depends(get_current_user_from_auth),
    db: Session = Depends(get_db),
):
    """Delete asset."""
    db_asset = db.query(Asset).filter(
        Asset.id == asset_id, Asset.user_id == current_user.id
    ).first()

    if not db_asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )

    db.delete(db_asset)
    db.commit()

    return SuccessResponse(
        success=True,
        message="Asset deleted successfully",
    )


@router.get("/summary", response_model=SuccessResponse)
def asset_summary(
    current_user: User = Depends(get_current_user_from_auth),
    db: Session = Depends(get_db),
):
    """Get asset summary."""
    assets = db.query(Asset).filter(Asset.user_id == current_user.id).all()
    total_value = sum(a.value for a in assets)

    summary = AssetSummary(
        total_value=total_value,
        asset_count=len(assets),
        net_worth=total_value,  # Simplified: actual calculation should subtract liabilities
        currency="USD",
    )

    return SuccessResponse(
        success=True,
        data=summary.model_dump(),
    )


@router.get("/distribution", response_model=SuccessResponse)
def asset_distribution(
    current_user: User = Depends(get_current_user_from_auth),
    db: Session = Depends(get_db),
):
    """Get asset distribution by type."""
    assets = db.query(Asset).filter(Asset.user_id == current_user.id).all()
    distribution = {}

    for asset in assets:
        asset_type = asset.asset_type.value
        if asset_type not in distribution:
            distribution[asset_type] = {"count": 0, "value": 0.0}
        distribution[asset_type]["count"] += 1
        distribution[asset_type]["value"] += asset.value

    return SuccessResponse(
        success=True,
        data=distribution,
    )


@router.get("/health-score", response_model=SuccessResponse)
def health_score(
    current_user: User = Depends(get_current_user_from_auth),
    db: Session = Depends(get_db),
):
    """Get asset health score."""
    assets = db.query(Asset).filter(Asset.user_id == current_user.id).all()

    # Simplified scoring logic
    diversification_score = min(90, len(assets) * 10) if len(assets) > 0 else 0
    liquidity_score = 75
    return_score = 70

    overall_score = int((diversification_score + liquidity_score + return_score) / 3)
    grade = "A" if overall_score >= 80 else "B" if overall_score >= 70 else "C"

    health = HealthScore(
        score=overall_score,
        grade=grade,
        factors=[
            HealthScoreFactor(name="资产分散度", score=diversification_score),
            HealthScoreFactor(name="流动性", score=liquidity_score),
            HealthScoreFactor(name="投资回报", score=return_score),
        ],
    )

    return SuccessResponse(
        success=True,
        data=health.model_dump(),
    )
