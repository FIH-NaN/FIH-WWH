from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.server.db.database import get_db
from src.server.db.db_gateway.user import search_user_by_id
from src.server.core.entities.user import User
from src.server.config import get_settings


settings = get_settings()
bearer_scheme = HTTPBearer(auto_error=False)


# Password hashing
# Use pbkdf2_sha256 to avoid bcrypt backend incompatibilities in this runtime.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[str]:
    """Decode JWT token and return user_id."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except JWTError:
        return None


def get_bearer_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
    """Extract Bearer token from Authorization header."""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return credentials.credentials


def get_current_user(
    token: str = Depends(get_bearer_token),
    db: Session = Depends(get_db),
) -> User:
    """Resolve current authenticated user from Bearer token."""
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user = search_user_by_id(db, int(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user
