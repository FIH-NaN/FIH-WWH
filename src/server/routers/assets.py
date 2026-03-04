from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models import Asset, User
from schemas import (
    AssetCreate,
    AssetResponse,
    AssetUpdate,
    SuccessResponse,
)
from core.dependencies import get_current_user
from services.asset_analytics_service import (
    calculate_asset_distribution,
    calculate_asset_summary,
)
from services.health_scoring_service import calculate_health_score

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("", response_model=SuccessResponse)
def list_assets(
    asset_type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get asset summary."""
    summary = calculate_asset_summary(db, current_user.id)

    return SuccessResponse(
        success=True,
        data=summary,
    )


@router.get("/distribution", response_model=SuccessResponse)
def asset_distribution(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get asset distribution by type."""
    distribution = calculate_asset_distribution(db, current_user.id)

    return SuccessResponse(
        success=True,
        data=distribution,
    )


@router.get("/health-score", response_model=SuccessResponse)
def health_score(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get asset health score."""
    health = calculate_health_score(db, current_user.id)

    return SuccessResponse(
        success=True,
        data=health,
    )
