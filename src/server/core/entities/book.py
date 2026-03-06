from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict

from src.server.core.entities.assets import Asset
from src.server.core.entities.liabilities import Liability
from src.server.core.entities.incomes import Income
from src.server.core.entities.expenses import Expense
from src.server.core.entities.cash_flows import CashFlow


@dataclass(slots=True)
class Book:
	"""Financial book/ledger for a user's accounts."""
	user_id: int
	created_at: datetime = field(default_factory=datetime.now)
	updated_at: datetime = field(default_factory=datetime.now)

	# Financial records
	assets: Dict[int, Asset] = field(default_factory=dict)
	liabilities: Dict[int, Liability] = field(default_factory=dict)
	incomes: Dict[int, Income] = field(default_factory=dict)
	expenses: Dict[int, Expense] = field(default_factory=dict)
	cash_flows: Dict[int, CashFlow] = field(default_factory=dict)

	def get_total_assets(self) -> float:
		"""Calculate total asset value."""
		return sum(asset.current_value() for asset in self.assets.values())

	def get_total_liabilities(self) -> float:
		"""Calculate total liability value."""
		return sum(liability.current_value() for liability in self.liabilities.values())

	def get_net_worth(self) -> float:
		"""Calculate net worth (assets - liabilities)."""
		return self.get_total_assets() - self.get_total_liabilities()

	def get_total_monthly_income(self) -> float:
		"""Calculate total monthly income."""
		return sum(income.monthly_amount() for income in self.incomes.values())

	def get_total_monthly_expenses(self) -> float:
		"""Calculate total monthly expenses."""
		return sum(expense.monthly_amount() for expense in self.expenses.values())

	def get_monthly_cash_flow(self) -> float:
		"""Calculate monthly cash flow (income - expenses)."""
		return self.get_total_monthly_income() - self.get_total_monthly_expenses()
