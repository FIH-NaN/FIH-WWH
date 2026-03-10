from typing import Optional, List, Dict
from sqlalchemy.orm import Session

from src.server.db.tables.assets import Asset
from src.server.db.db_gateway.assets import (
    get_next_asset_id,
    get_current_asset_index,
    get_asset_count,
    get_all_assets,
    get_asset_by_id,
)
from src.server.core.entities.assets import AssetCategory
from src.server.services.financial_analysis.wellness_metrics import WellnessMetricsService


class UserAssetDataManager:
	"""Manager for user asset data operations."""

	@staticmethod
	def list_assets(
		db: Session,
		user_id: int,
		asset_type: Optional[str] = None,
		category: Optional[str] = None,
		page: int = 1,
		limit: int = 10,
	) -> tuple[List[Asset], int]:
		"""
		List all assets for a user with optional filters.
		
		Args:
		    db: Database session
		    user_id: The user ID
		    asset_type: Filter by asset type (AssetCategory)
		    category: Filter by user-defined category
		    page: Page number (1-indexed)
		    limit: Items per page
		    
		Returns:
		    Tuple of (assets list, total count)
		"""
		query = db.query(Asset).filter(Asset.user_id == user_id)

		if asset_type:
			query = query.filter(Asset.asset_type == asset_type)
		if category:
			query = query.filter(Asset.category == category)

		total = query.count()
		assets = query.offset((page - 1) * limit).limit(limit).all()

		return assets, total

	@staticmethod
	def create_asset(
		db: Session,
		user_id: int,
		name: str,
		asset_type: AssetCategory,
		value: float,
		currency: str = "USD",
		category: str = "",
		description: str = "",
	) -> Asset:
		"""
		Create a new asset for a user.
		
		Args:
		    db: Database session
		    user_id: The user ID
		    name: Asset name
		    asset_type: Asset type (AssetCategory)
		    value: Asset value
		    currency: Currency code
		    category: User-defined category
		    description: Asset description
		    
		Returns:
		    The created Asset object
		"""
		asset_id = get_next_asset_id(db, user_id)
		
		new_asset = Asset(
			id=asset_id,
			user_id=user_id,
			name=name,
			asset_type=asset_type,
			value=value,
			currency=currency,
			category=category,
			description=description,
		)
		
		db.add(new_asset)
		db.commit()
		db.refresh(new_asset)
		
		return new_asset

	@staticmethod
	def get_asset(db: Session, user_id: int, asset_id: int) -> Optional[Asset]:
		"""
		Get a specific asset by user_id and asset_id.
		
		Args:
		    db: Database session
		    user_id: The user ID
		    asset_id: The asset ID
		    
		Returns:
		    Asset object or None if not found
		"""
		return get_asset_by_id(db, user_id, asset_id)

	@staticmethod
	def update_asset(
		db: Session,
		user_id: int,
		asset_id: int,
		name: Optional[str] = None,
		value: Optional[float] = None,
		description: Optional[str] = None,
		category: Optional[str] = None,
	) -> Optional[Asset]:
		"""
		Update an asset.
		
		Args:
		    db: Database session
		    user_id: The user ID
		    asset_id: The asset ID
		    name: New asset name
		    value: New asset value
		    description: New asset description
		    category: New asset category
		    
		Returns:
		    Updated Asset object or None if not found
		"""
		db_asset = get_asset_by_id(db, user_id, asset_id)
		if not db_asset:
			return None

		if name:
			db_asset.name = name
		if value is not None:
			db_asset.value = value
		if description:
			db_asset.description = description
		if category:
			db_asset.category = category

		db.commit()
		db.refresh(db_asset)

		return db_asset

	@staticmethod
	def delete_asset(db: Session, user_id: int, asset_id: int) -> bool:
		"""
		Delete an asset.
		
		Args:
		    db: Database session
		    user_id: The user ID
		    asset_id: The asset ID
		    
		Returns:
		    True if deleted, False if not found
		"""
		db_asset = get_asset_by_id(db, user_id, asset_id)
		if not db_asset:
			return False

		db.delete(db_asset)
		db.commit()

		return True

	@staticmethod
	def get_asset_summary(db: Session, user_id: int) -> Dict:
		"""
		Get asset summary for a user.
		
		Args:
		    db: Database session
		    user_id: The user ID
		    
		Returns:
		    Dictionary with total_value, asset_count, currency
		"""
		assets = get_all_assets(db, user_id)
		total_value = sum(a.value for a in assets)
		
		return {
			"total_value": total_value,
			"asset_count": len(assets),
			"net_worth": total_value,  # Simplified: actual calculation should subtract liabilities
			"currency": "USD",
		}

	@staticmethod
	def get_asset_distribution(db: Session, user_id: int) -> Dict:
		"""
		Get asset distribution by type.
		
		Args:
		    db: Database session
		    user_id: The user ID
		    
		Returns:
		    Dictionary with distribution data by asset type
		"""
		assets = get_all_assets(db, user_id)
		distribution = {}

		for asset in assets:
			asset_type = asset.asset_type.value if hasattr(asset.asset_type, 'value') else str(asset.asset_type)
			if asset_type not in distribution:
				distribution[asset_type] = {"count": 0, "value": 0.0}
			distribution[asset_type]["count"] += 1
			distribution[asset_type]["value"] += asset.value

		return distribution

	@staticmethod
	def get_health_score(db: Session, user_id: int) -> Dict:
		"""
		Get asset health score.
		
		Args:
		    db: Database session
		    user_id: The user ID
		    
		Returns:
		    Dictionary with score, grade, and factors
		"""
		overview = WellnessMetricsService.build_overview(db=db, user_id=user_id)

		return {
			"score": overview["overall_score"],
			"grade": overview["grade"],
			"factors": [
				{"name": factor["name"], "score": factor["score"]}
				for factor in overview["factors"]
			],
		}

	@staticmethod
	def get_wealth_overview(db: Session, user_id: int) -> Dict:
		"""Get factorized wellness overview for dashboard and advisor surfaces."""
		return WellnessMetricsService.build_overview(db=db, user_id=user_id)

	@staticmethod
	def get_wealth_insights(db: Session, user_id: int) -> Dict:
		"""Get latest cached AI insights only (no model invocation)."""
		return WellnessMetricsService.build_ai_insights(db=db, user_id=user_id)

	@staticmethod
	def refresh_wealth_insights(db: Session, user_id: int) -> Dict:
		"""Manually regenerate AI insights and persist a new history row."""
		return WellnessMetricsService.refresh_ai_insights(db=db, user_id=user_id)

	@staticmethod
	def get_wealth_insights_history(db: Session, user_id: int, limit: int = 10) -> Dict:
		"""List stored AI insights history for longitudinal comparison."""
		return WellnessMetricsService.list_ai_insights_history(db=db, user_id=user_id, limit=limit)

	@staticmethod
	def get_portfolio_analysis(db: Session, user_id: int) -> Dict:
		"""Get portfolio composition, 12-month performance, and frontier analysis."""
		return WellnessMetricsService.build_portfolio_analysis(db=db, user_id=user_id)
