from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .assets import Asset, AssetCategory
from .cash_flows import CashFlow
from .expenses import Expense
from .incomes import Income
from .liabilities import Liability


@dataclass(slots=True)
class WealthWallet:
	name: str = "Primary Wallet"
	base_currency: str = "USD"
	assets: List[Asset] = field(default_factory=list)
	liabilities: List[Liability] = field(default_factory=list)
	incomes: List[Income] = field(default_factory=list)
	expenses: List[Expense] = field(default_factory=list)
	cash_flows: List[CashFlow] = field(default_factory=list)

	def add_asset(self, asset: Asset) -> None:
		self.assets.append(asset)

	def add_liability(self, liability: Liability) -> None:
		self.liabilities.append(liability)

	def add_income(self, income: Income) -> None:
		self.incomes.append(income)

	def add_expense(self, expense: Expense) -> None:
		self.expenses.append(expense)

	def add_cash_flow(self, cash_flow: CashFlow) -> None:
		self.cash_flows.append(cash_flow)

	def total_assets(self) -> float:
		return sum(asset.current_value() for asset in self.assets)

	def total_liabilities(self) -> float:
		return sum(liability.current_value() for liability in self.liabilities)

	def net_worth(self) -> float:
		return self.total_assets() - self.total_liabilities()

	def liquid_assets(self) -> float:
		return sum(asset.current_value() for asset in self.assets if asset.is_liquid())

	def liquidity_ratio(self) -> float:
		liabilities = self.total_liabilities()
		if liabilities <= 0:
			return float("inf")
		return self.liquid_assets() / liabilities

	def total_monthly_income(self) -> float:
		return sum(income.monthly_amount() for income in self.incomes)

	def total_monthly_expense(self) -> float:
		return sum(expense.monthly_amount() for expense in self.expenses)

	def monthly_surplus(self) -> float:
		return self.total_monthly_income() - self.total_monthly_expense()

	def savings_rate(self) -> float:
		total_income = self.total_monthly_income()
		if total_income <= 0:
			return 0.0
		return self.monthly_surplus() / total_income

	def asset_allocation(self) -> Dict[AssetCategory, float]:
		total_assets = self.total_assets()
		if total_assets <= 0:
			return {}

		allocation: Dict[AssetCategory, float] = {}
		for asset in self.assets:
			allocation[asset.category] = allocation.get(asset.category, 0.0) + asset.current_value()

		return {category: value / total_assets for category, value in allocation.items()}

	def debt_to_asset_ratio(self) -> float:
		total_assets = self.total_assets()
		if total_assets <= 0:
			return float("inf") if self.total_liabilities() > 0 else 0.0
		return self.total_liabilities() / total_assets

	def to_summary(self) -> Dict[str, float]:
		return {
			"total_assets": self.total_assets(),
			"total_liabilities": self.total_liabilities(),
			"net_worth": self.net_worth(),
			"liquid_assets": self.liquid_assets(),
			"liquidity_ratio": self.liquidity_ratio(),
			"total_monthly_income": self.total_monthly_income(),
			"total_monthly_expense": self.total_monthly_expense(),
			"monthly_surplus": self.monthly_surplus(),
			"savings_rate": self.savings_rate(),
			"debt_to_asset_ratio": self.debt_to_asset_ratio(),
		}