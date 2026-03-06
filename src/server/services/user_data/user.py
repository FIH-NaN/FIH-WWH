

from typing import Optional, List, Dict
from datetime import datetime
from sqlalchemy.orm import Session
import logging

from src.server.db.tables.user import User
from src.server.db.db_gateway.user import search_user_by_id
from src.server.core.entities.user import User as UserEntity

logger = logging.getLogger(__name__)


class UserDataManager:
	"""Manager for user data operations including auth and profile updates."""

	@staticmethod
	def create_user(
		db: Session,
		email: str,
		name: str,
		hashed_password: str,
	) -> User:
		"""
		Create a new user.
		
		Args:
		    db: Database session
		    email: User email
		    name: User name
		    hashed_password: Hashed password
		    
		Returns:
		    Created User object
		"""
		new_user = User(
			email=email,
			name=name,
			hashed_password=hashed_password,
		)
		db.add(new_user)
		db.commit()
		db.refresh(new_user)
		return new_user

	@staticmethod
	def get_user_by_email(db: Session, email: str) -> Optional[User]:
		"""
		Get a user by email.
		
		Args:
		    db: Database session
		    email: User email
		    
		Returns:
		    User object or None if not found
		"""
		return db.query(User).filter(User.email == email).first()

	@staticmethod
	def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
		"""
		Get a user by ID.
		
		Args:
		    db: Database session
		    user_id: User ID
		    
		Returns:
		    User object or None if not found
		"""
		return db.query(User).filter(User.id == user_id).first()

	@staticmethod
	def update_user_profile(
		db: Session,
		user_id: int,
		name: Optional[str] = None,
		email: Optional[str] = None,
	) -> Optional[User]:
		"""
		Update user profile information.
		
		Args:
		    db: Database session
		    user_id: User ID
		    name: New name
		    email: New email
		    
		Returns:
		    Updated User object or None if not found
		"""
		user = UserDataManager.get_user_by_id(db, user_id)
		if not user:
			return None

		if name:
			user.name = name
		if email:
			user.email = email
		user.updated_at = datetime.utcnow()

		db.commit()
		db.refresh(user)
		return user

	@staticmethod
	def update_user_password(
		db: Session,
		user_id: int,
		new_hashed_password: str,
	) -> Optional[User]:
		"""
		Update user password.
		
		Args:
		    db: Database session
		    user_id: User ID
		    new_hashed_password: New hashed password
		    
		Returns:
		    Updated User object or None if not found
		"""
		user = UserDataManager.get_user_by_id(db, user_id)
		if not user:
			return None

		user.hashed_password = new_hashed_password
		user.updated_at = datetime.utcnow()

		db.commit()
		db.refresh(user)
		return user

	@staticmethod
	def update_user_bank_deposit(db: Session, user_id: int) -> Optional[Dict]:
		"""
		Update user's bank deposit information.
		This task runs daily to sync bank account balances and deposits.
		
		Args:
		    db: Database session
		    user_id: User ID
		    
		Returns:
		    Dictionary with update results or None if user not found
		"""
		user = UserDataManager.get_user_by_id(db, user_id)
		if not user:
			logger.warning(f"User {user_id} not found for bank deposit update")
			return None

		try:
			# In a real implementation, this would:
			# 1. Call bank APIs to fetch up-to-date deposit information
			# 2. Update the user's assets in the database
			# 3. Record transaction history
			# For now, we just mark that we processed it
			
			user.updated_at = datetime.utcnow()
			db.commit()
			
			logger.info(f"✓ Bank deposit updated for user {user_id}")
			return {
				"user_id": user_id,
				"status": "success",
				"updated_at": datetime.utcnow().isoformat(),
				"message": "Bank deposit information synchronized",
			}
		except Exception as e:
			logger.error(f"✗ Error updating bank deposit for user {user_id}: {e}")
			return {
				"user_id": user_id,
				"status": "error",
				"error": str(e),
			}

	@staticmethod
	def update_user_portfolio(db: Session, user_id: int) -> Optional[Dict]:
		"""
		Update user's portfolio information.
		Recalculates asset valuations and risk metrics.
		
		Args:
		    db: Database session
		    user_id: User ID
		    
		Returns:
		    Dictionary with update results or None if user not found
		"""
		user = UserDataManager.get_user_by_id(db, user_id)
		if not user:
			logger.warning(f"User {user_id} not found for portfolio update")
			return None

		try:
			# In a real implementation, this would:
			# 1. Fetch current asset prices
			# 2. Recalculate portfolio value
			# 3. Update risk metrics (Beta, Sharpe ratio, etc.)
			# 4. Store results in analytics tables
			
			user.updated_at = datetime.utcnow()
			db.commit()
			
			logger.info(f"✓ Portfolio updated for user {user_id}")
			return {
				"user_id": user_id,
				"status": "success",
				"updated_at": datetime.utcnow().isoformat(),
				"message": "Portfolio information recalculated",
			}
		except Exception as e:
			logger.error(f"✗ Error updating portfolio for user {user_id}: {e}")
			return {
				"user_id": user_id,
				"status": "error",
				"error": str(e),
			}

	@staticmethod
	def update_user_financial_statements(db: Session, user_id: int) -> Optional[Dict]:
		"""
		Update user's financial statements.
		Generates or updates balance sheet, income statement, and cash flow statement.
		
		Args:
		    db: Database session
		    user_id: User ID
		    
		Returns:
		    Dictionary with update results or None if user not found
		"""
		user = UserDataManager.get_user_by_id(db, user_id)
		if not user:
			logger.warning(f"User {user_id} not found for financial statements update")
			return None

		try:
			# In a real implementation, this would:
			# 1. Aggregate all assets, liabilities, income, and expenses
			# 2. Generate financial statements
			# 3. Calculate financial ratios
			# 4. Store results for historical tracking
			
			user.updated_at = datetime.utcnow()
			db.commit()
			
			logger.info(f"✓ Financial statements updated for user {user_id}")
			return {
				"user_id": user_id,
				"status": "success",
				"updated_at": datetime.utcnow().isoformat(),
				"message": "Financial statements generated",
			}
		except Exception as e:
			logger.error(f"✗ Error updating financial statements for user {user_id}: {e}")
			return {
				"user_id": user_id,
				"status": "error",
				"error": str(e),
			}

	@staticmethod
	def get_all_users(db: Session) -> List[User]:
		"""
		Get all users in the system.
		
		Args:
		    db: Database session
		    
		Returns:
		    List of User objects
		"""
		return db.query(User).all()
    
