from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from core.dependencies import get_current_user
from db.database import get_db
from db.db_models import Category, User
from db.schemas import (
    CategoryCreate,
    CategoryResponse,
    SuccessResponse,
)

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=SuccessResponse)
def list_categories(
    category_type: Optional[str] = Query(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get list of categories."""
    query = db.query(Category).filter(Category.user_id == user.id)

    if category_type:
        query = query.filter(Category.category_type == category_type)

    categories = query.all()

    return SuccessResponse(
        success=True,
        data={
            "categories": [CategoryResponse.model_validate(c).model_dump() for c in categories]
        },
    )


@router.post("", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category: CategoryCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new category."""
    new_category = Category(
        user_id=user.id,
        name=category.name,
        category_type=category.category_type,
        icon=category.icon,
    )
    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return SuccessResponse(
        success=True,
        data=CategoryResponse.model_validate(new_category).model_dump(),
    )
