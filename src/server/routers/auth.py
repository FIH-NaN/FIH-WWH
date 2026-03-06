from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.server.services.user_data.user import UserDataManager
from src.server.services.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)
from src.server.db.database import get_db
from src.server.db.tables.user import User
from src.server.routers.web_view_model.schemas import (
    UserResponse,
    LoginRequest,
    RegisterRequest,
    SuccessResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=SuccessResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user exists
    existing_user = UserDataManager.get_user_by_email(db, request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    hashed_pwd = hash_password(request.password)
    new_user = UserDataManager.create_user(
        db=db,
        email=request.email,
        name=request.name,
        hashed_password=hashed_pwd,
    )

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
    user = UserDataManager.get_user_by_email(db, request.email)
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
def get_me(current_user: User = Depends(get_current_user)):
    """Get current user."""
    return SuccessResponse(
        success=True,
        data=UserResponse.model_validate(current_user).model_dump(),
    )
