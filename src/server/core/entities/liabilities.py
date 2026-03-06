from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import List, Optional

from src.server.core.entities.currency import Currency
from src.server.core.entities.object import FinancialObject

class LiabilityCategory(str, Enum):
		MORTGAGE = "mortgage"
		LOAN = "loan"
		CREDIT_CARD = "credit_card"
		TAX = "tax"
		OTHER = "other"


@dataclass(slots=True)
class Liability(FinancialObject):
		"""
		A liability class
		"""
		name: str
		category: LiabilityCategory
		principal: float
		outstanding_balance: float
		currency: Currency

		annual_interest_rate: float = 0.0
		minimum_payment: float = 0.0
		due_date: Optional[date] = None
		lender: str = ""
		tags: List[str] = field(default_factory=list)

		def current_value(self) -> float:
				return self.outstanding_balance

