# Copyright (c) 2026

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from src.server.core.entities.common import RecurringFrequency
from src.server.core.entities.object import FinancialObject
from src.server.core.entities.currency import Currency


class IncomeType(str, Enum):
		SALARY = "salary"
		BONUS = "bonus"
		FREELANCE = "freelance"
		DIVIDEND = "dividend"
		INTEREST = "interest"
		RENTAL = "rental"
		BUSINESS = "business"
		OTHER = "other"


@dataclass(slots=True)
class Income(FinancialObject):
		"""
		Income 
		"""

		id: int
		name: str
		income_type: IncomeType
		amount: float
		currency: Currency
		cash_flow_id: int

		frequency: RecurringFrequency = RecurringFrequency.MONTHLY
		source: str = ""
		is_taxable: bool = True

		def monthly_amount(self) -> float:
				factors = {
						RecurringFrequency.ONCE: 0.0,
						RecurringFrequency.WEEKLY: 52 / 12,
						RecurringFrequency.BIWEEKLY: 26 / 12,
						RecurringFrequency.MONTHLY: 1.0,
						RecurringFrequency.QUARTERLY: 1 / 3,
						RecurringFrequency.YEARLY: 1 / 12,
				}
				return self.amount * factors[self.frequency]

		def annual_amount(self) -> float:
				return self.monthly_amount() * 12


