from typing import Optional

from fastapi import Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.security import decode_access_token
from database import get_db
from models import User


def resolve_token(authorization: Optional[str], token: Optional[str]) -> Optional[str]:
    """Resolve token from Bearer header first, then query fallback."""
    if authorization:
        if authorization.startswith("Bearer "):
            return authorization.split(" ", 1)[1]
        return authorization
    return token


def get_current_user(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db),
) -> User:
    """Shared dependency to authenticate user from JWT token."""
    resolved_token = resolve_token(authorization, token)
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

    return user
