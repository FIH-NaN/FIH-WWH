from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from src.server.services.user_data.asset_data import UserAssetDataManager
from src.server.services.auth.security import get_current_user
from src.server.db.database import get_db
from src.server.db.tables.user import User
from src.server.routers.web_view_model.schemas import (
    AssetCreate,
    AssetResponse,
    AssetUpdate,
    AssetSummary,
    HealthScore,
    HealthScoreFactor,
    SuccessResponse,
)


router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("", response_model=SuccessResponse)
def list_assets(
    asset_type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get list of assets."""
    assets, total = UserAssetDataManager.list_assets(
        db=db,
        user_id=user.id,
        asset_type=asset_type,
        category=category,
        page=page,
        limit=limit
    )

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
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new asset."""
    new_asset = UserAssetDataManager.create_asset(
        db=db,
        user_id=user.id,
        name=asset.name,
        asset_type=asset.asset_type,
        value=asset.value,
        currency=asset.currency,
        category=asset.category,
        description=asset.description,
    )

    return SuccessResponse(
        success=True,
        data=AssetResponse.model_validate(new_asset).model_dump(),
    )


@router.get("/{asset_id}", response_model=SuccessResponse)
def get_asset(
    asset_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get single asset by ID."""
    asset = UserAssetDataManager.get_asset(db=db, user_id=user.id, asset_id=asset_id)

    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )

    return SuccessResponse(
        success=True,
        data=AssetResponse.model_validate(asset).model_dump(),
    )


@router.put("/{asset_id}", response_model=SuccessResponse)
def update_asset(
    asset_id: int,
    asset: AssetUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update asset."""
    db_asset = UserAssetDataManager.update_asset(
        db=db,
        user_id=user.id,
        asset_id=asset_id,
        name=asset.name,
        value=asset.value,
        description=asset.description,
    )

    if not db_asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )

    return SuccessResponse(
        success=True,
        data=AssetResponse.model_validate(db_asset).model_dump(),
    )


@router.delete("/{asset_id}", response_model=SuccessResponse)
def delete_asset(
    asset_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete asset."""
    deleted = UserAssetDataManager.delete_asset(db=db, user_id=user.id, asset_id=asset_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )

    return SuccessResponse(
        success=True,
        message="Asset deleted successfully",
    )


@router.get("/summary", response_model=SuccessResponse)
def asset_summary(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get asset summary."""
    summary_data = UserAssetDataManager.get_asset_summary(db=db, user_id=user.id)

    summary = AssetSummary(
        total_value=summary_data["total_value"],
        asset_count=summary_data["asset_count"],
        net_worth=summary_data["net_worth"],
        currency=summary_data["currency"],
    )

    return SuccessResponse(
        success=True,
        data=summary.model_dump(),
    )


@router.get("/distribution", response_model=SuccessResponse)
def asset_distribution(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get asset distribution by type."""
    distribution = UserAssetDataManager.get_asset_distribution(db=db, user_id=user.id)

    return SuccessResponse(
        success=True,
        data=distribution,
    )


@router.get("/health-score", response_model=SuccessResponse)
def health_score(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get asset health score."""
    health_data = UserAssetDataManager.get_health_score(db=db, user_id=user.id)

    health = HealthScore(
        score=health_data["score"],
        grade=health_data["grade"],
        factors=[
            HealthScoreFactor(name=f["name"], score=f["score"])
            for f in health_data["factors"]
        ],
    )

    return SuccessResponse(
        success=True,
        data=health.model_dump(),
    )
