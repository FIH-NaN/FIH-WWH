from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from .assets import Asset, AssetCategory
from .expenses import Expense
from .incomes import Income
from .liabilities import Liability


@dataclass(slots=True)
class Portfolio:
    """
    A user's complete portfolio containing all their assets, liabilities, incomes, and expenses.
    Maintains mappings of user_id to asset IDs for efficient lookups.
    """
    user_id: int
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    # Asset holdings: maps asset_id -> Asset
    assets: Dict[int, Asset] = field(default_factory=dict)
    # User's asset IDs: maps user_id -> list of asset_ids
    user_asset_ids: Dict[int, List[int]] = field(default_factory=dict)

    # Liability holdings: maps liability_id -> Liability
    liabilities: Dict[int, Liability] = field(default_factory=dict)
    # User's liability IDs: maps user_id -> list of liability_ids
    user_liability_ids: Dict[int, List[int]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize default entry for user_id if not present."""
        if self.user_id not in self.user_asset_ids:
          self.user_asset_ids[self.user_id] = []
        if self.user_id not in self.user_liability_ids:
          self.user_liability_ids[self.user_id] = []

    def add_asset(self, asset_id: int, asset: Asset, user_id: Optional[int] = None) -> None:
        """Add an asset to the portfolio."""
        if user_id is None:
          user_id = self.user_id
        self.assets[asset_id] = asset
        if user_id not in self.user_asset_ids:
          self.user_asset_ids[user_id] = []
        if asset_id not in self.user_asset_ids[user_id]:
          self.user_asset_ids[user_id].append(asset_id)
        self.updated_at = datetime.now()

    def remove_asset(self, asset_id: int, user_id: Optional[int] = None) -> None:
        """Remove an asset from the portfolio."""
        if user_id is None:
          user_id = self.user_id
        if asset_id in self.assets:
          del self.assets[asset_id]
        if user_id in self.user_asset_ids and asset_id in self.user_asset_ids[user_id]:
          self.user_asset_ids[user_id].remove(asset_id)
        self.updated_at = datetime.now()

	  def get_user_assets(self, user_id: Optional[int] = None) -> List[Asset]:
      """Get all assets for a specific user."""
      if user_id is None:
        user_id = self.user_id
      asset_ids = self.user_asset_ids.get(user_id, [])
      return [self.assets[aid] for aid in asset_ids if aid in self.assets]

	def add_liability(self, liability_id: int, liability: Liability, user_id: Optional[int] = None) -> None:
		"""Add a liability to the portfolio."""
		if user_id is None:
			user_id = self.user_id
		self.liabilities[liability_id] = liability
		if user_id not in self.user_liability_ids:
			self.user_liability_ids[user_id] = []
		if liability_id not in self.user_liability_ids[user_id]:
			self.user_liability_ids[user_id].append(liability_id)
		self.updated_at = datetime.now()

	def remove_liability(self, liability_id: int, user_id: Optional[int] = None) -> None:
		"""Remove a liability from the portfolio."""
		if user_id is None:
			user_id = self.user_id
		if liability_id in self.liabilities:
			del self.liabilities[liability_id]
		if user_id in self.user_liability_ids and liability_id in self.user_liability_ids[user_id]:
			self.user_liability_ids[user_id].remove(liability_id)
		self.updated_at = datetime.now()

	def get_user_liabilities(self, user_id: Optional[int] = None) -> List[Liability]:
		"""Get all liabilities for a specific user."""
		if user_id is None:
			user_id = self.user_id
		liability_ids = self.user_liability_ids.get(user_id, [])
		return [self.liabilities[lid] for lid in liability_ids if lid in self.liabilities]

	def add_income(self, income_id: int, income: Income, user_id: Optional[int] = None) -> None:
		"""Add an income stream to the portfolio."""
		if user_id is None:
			user_id = self.user_id
		self.incomes[income_id] = income
		if user_id not in self.user_income_ids:
			self.user_income_ids[user_id] = []
		if income_id not in self.user_income_ids[user_id]:
			self.user_income_ids[user_id].append(income_id)
		self.updated_at = datetime.now()

	def remove_income(self, income_id: int, user_id: Optional[int] = None) -> None:
		"""Remove an income stream from the portfolio."""
		if user_id is None:
			user_id = self.user_id
		if income_id in self.incomes:
			del self.incomes[income_id]
		if user_id in self.user_income_ids and income_id in self.user_income_ids[user_id]:
			self.user_income_ids[user_id].remove(income_id)
		self.updated_at = datetime.now()

	def get_user_incomes(self, user_id: Optional[int] = None) -> List[Income]:
		"""Get all income streams for a specific user."""
		if user_id is None:
			user_id = self.user_id
		income_ids = self.user_income_ids.get(user_id, [])
		return [self.incomes[iid] for iid in income_ids if iid in self.incomes]

	def add_expense(self, expense_id: int, expense: Expense, user_id: Optional[int] = None) -> None:
		"""Add an expense to the portfolio."""
		if user_id is None:
			user_id = self.user_id
		self.expenses[expense_id] = expense
		if user_id not in self.user_expense_ids:
			self.user_expense_ids[user_id] = []
		if expense_id not in self.user_expense_ids[user_id]:
			self.user_expense_ids[user_id].append(expense_id)
		self.updated_at = datetime.now()

	def remove_expense(self, expense_id: int, user_id: Optional[int] = None) -> None:
		"""Remove an expense from the portfolio."""
		if user_id is None:
			user_id = self.user_id
		if expense_id in self.expenses:
			del self.expenses[expense_id]
		if user_id in self.user_expense_ids and expense_id in self.user_expense_ids[user_id]:
			self.user_expense_ids[user_id].remove(expense_id)
		self.updated_at = datetime.now()

	def get_user_expenses(self, user_id: Optional[int] = None) -> List[Expense]:
		"""Get all expenses for a specific user."""
		if user_id is None:
			user_id = self.user_id
		expense_ids = self.user_expense_ids.get(user_id, [])
		return [self.expenses[eid] for eid in expense_ids if eid in self.expenses]

	def get_total_asset_value(self, user_id: Optional[int] = None) -> float:
		"""Calculate total value of all assets for a user."""
		assets = self.get_user_assets(user_id)
		return sum(asset.current_value() for asset in assets)

	def get_total_liability_value(self, user_id: Optional[int] = None) -> float:
		"""Calculate total value of all liabilities for a user."""
		liabilities = self.get_user_liabilities(user_id)
		return sum(liability.current_value() for liability in liabilities)

	def get_net_worth(self, user_id: Optional[int] = None) -> float:
		"""Calculate net worth (assets - liabilities)."""
		return self.get_total_asset_value(user_id) - self.get_total_liability_value(user_id)

	def get_asset_distribution(self, user_id: Optional[int] = None) -> Dict[AssetCategory, float]:
		"""Get asset distribution by category."""
		assets = self.get_user_assets(user_id)
		distribution: Dict[AssetCategory, float] = {}
		for asset in assets:
			category = asset.category
			distribution[category] = distribution.get(category, 0.0) + asset.current_value()
		return distribution

	def get_monthly_cash_flow(self, user_id: Optional[int] = None) -> float:
		"""Calculate monthly cash flow (incomes - expenses)."""
		incomes = self.get_user_incomes(user_id)
		expenses = self.get_user_expenses(user_id)
		
		total_income = sum(income.monthly_amount() for income in incomes)
		total_expenses = sum(expense.monthly_amount() for expense in expenses)
		
		return total_income - total_expenses

	def get_annual_cash_flow(self, user_id: Optional[int] = None) -> float:
		"""Calculate annual cash flow (incomes - expenses)."""
		return self.get_monthly_cash_flow(user_id) * 12
