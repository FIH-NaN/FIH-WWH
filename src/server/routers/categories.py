from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models import Category, User
from schemas import (
    CategoryCreate,
    CategoryResponse,
    SuccessResponse,
)
from core.security import decode_access_token

router = APIRouter(prefix="/categories", tags=["categories"])


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


@router.get("", response_model=SuccessResponse)
def list_categories(
    category_type: Optional[str] = Query(None),
    token: str = None,
    db: Session = Depends(get_db),
):
    """Get list of categories."""
    user = get_current_user(token, db)

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
    token: str = None,
    db: Session = Depends(get_db),
):
    """Create a new category."""
    user = get_current_user(token, db)

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
