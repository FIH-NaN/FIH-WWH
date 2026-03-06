from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Iterable

from src.server.core.entities.currency import Currency


class CashFlowType(str, Enum):
		""" A cash flow is either inflow or outflow """
		INFLOW = "inflow"
		OUTFLOW = "outflow"


@dataclass(slots=True)
class CashFlow:
		"""
		Cash flow of a user

		It should not be a financial object but rather a documentation 
			of a financial object.
		
		The cash flow should be stored as a key-value database rather than a time
			series database.
		"""
		id: int
		event_date: date
		flow_type: CashFlowType
		amount: float
		currency: Currency
		related_asset_id: int

		description: str = ""
		category: str = ""
		
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
