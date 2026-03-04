from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RecurringFrequency(str, Enum):
	ONCE = "once"
	WEEKLY = "weekly"
	BIWEEKLY = "biweekly"
	MONTHLY = "monthly"
	QUARTERLY = "quarterly"
	YEARLY = "yearly"


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
class Income:
	name: str
	income_type: IncomeType
	amount: float
	frequency: RecurringFrequency = RecurringFrequency.MONTHLY
	source: str = ""
	currency: str = "USD"
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
