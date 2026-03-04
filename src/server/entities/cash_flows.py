from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Iterable


class CashFlowType(str, Enum):
	INFLOW = "inflow"
	OUTFLOW = "outflow"
	TRANSFER = "transfer"


@dataclass(slots=True)
class CashFlow:
	event_date: date
	flow_type: CashFlowType
	amount: float
	description: str = ""
	category: str = ""
	currency: str = "USD"
	related_asset_name: str = ""

	def signed_amount(self) -> float:
		if self.flow_type == CashFlowType.INFLOW:
			return abs(self.amount)
		if self.flow_type == CashFlowType.OUTFLOW:
			return -abs(self.amount)
		return 0.0


@dataclass(slots=True)
class CashFlowSummary:
	@staticmethod
	def net_cash_flow(flows: Iterable[CashFlow]) -> float:
		return sum(flow.signed_amount() for flow in flows)

	@staticmethod
	def savings_rate(total_income: float, total_expense: float) -> float:
		if total_income <= 0:
			return 0.0
		return (total_income - total_expense) / total_income
