# todo : create user database related logic:
# e.g. check existence, search and return as core.entities.user data
from typing import Optional

from sqlalchemy.orm import Session

from src.server.db.tables.user import User


def search_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    """
    return db.get(User, user_id)


