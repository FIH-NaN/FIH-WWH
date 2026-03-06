from typing import Optional
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.server.db.tables.assets import Asset
from src.server.core.entities.assets import (
    Asset as AssetEntity,
    DepositAccount,
    DigitalAsset,
    Stock,
    ETF,
    AssetCategory,
)


def get_next_asset_id(db: Session, user_id: int) -> int:
	"""
	Get the next asset ID for a user (current max + 1).
	Returns 1 if the user has no assets yet.
	
	Args:
	    db: Database session
	    user_id: The user ID
	    
	Returns:
	    The next available asset ID for this user
	"""
	max_id = db.query(func.max(Asset.id)).filter(Asset.user_id == user_id).scalar()
	if max_id is None:
		return 1
	return max_id + 1


def get_current_asset_index(db: Session, user_id: int) -> int:
	"""
	Get the current highest asset index (ID) for a user.
	Returns 0 if the user has no assets.
	
	Args:
	    db: Database session
	    user_id: The user ID
	    
	Returns:
	    The current highest asset ID for this user
	"""
	max_id = db.query(func.max(Asset.id)).filter(Asset.user_id == user_id).scalar()
	if max_id is None:
		return 0
	return max_id


def get_asset_count(db: Session, user_id: int) -> int:
	"""
	Get the total number of assets for a user.
	
	Args:
	    db: Database session
	    user_id: The user ID
	    
	Returns:
	    The count of assets for this user
	"""
	return db.query(func.count(Asset.id)).filter(Asset.user_id == user_id).scalar()


def get_all_assets(db: Session, user_id: int) -> list:
	"""
	Get all assets for a user.
	
	Args:
	    db: Database session
	    user_id: The user ID
	    
	Returns:
	    List of Asset objects for the user
	"""
	return db.query(Asset).filter(Asset.user_id == user_id).all()


def get_asset_by_id(db: Session, user_id: int, asset_id: int) -> Optional[Asset]:
	"""
	Get a specific asset by user_id and asset_id.
	
	Args:
	    db: Database session
	    user_id: The user ID
	    asset_id: The asset ID (per-user)
	    
	Returns:
	    Asset object or None if not found
	"""
	return db.query(Asset).filter(
		Asset.user_id == user_id,
		Asset.id == asset_id
	).first()


