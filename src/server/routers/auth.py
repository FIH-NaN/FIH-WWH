from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import timedelta
from database import get_db
from models import User
from schemas import (
    UserCreate,
    UserResponse,
    Token,
    LoginRequest,
    RegisterRequest,
    SuccessResponse,
)
from core.security import hash_password, verify_password, create_access_token, decode_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=SuccessResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    hashed_pwd = hash_password(request.password)
    new_user = User(email=request.email, name=request.name, hashed_password=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create token
    access_token = create_access_token(data={"sub": str(new_user.id)})

    return SuccessResponse(
        success=True,
        data={
            "user": UserResponse.model_validate(new_user).model_dump(),
            "token": access_token,
        },
    )


@router.post("/login", response_model=SuccessResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login user."""
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = create_access_token(data={"sub": str(user.id)})

    return SuccessResponse(
        success=True,
        data={
            "token": access_token,
            "user": UserResponse.model_validate(user).model_dump(),
        },
    )


@router.get("/me", response_model=SuccessResponse)
def get_current_user(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Get current user."""
    resolved_token = token
    if authorization:
        resolved_token = authorization.split(" ", 1)[1] if authorization.startswith("Bearer ") else authorization

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

    return SuccessResponse(
        success=True,
        data=UserResponse.model_validate(user).model_dump(),
    )
