from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from src.server.core.entities.common import RecurringFrequency
from src.server.core.entities.financials.object import FinancialObject

class ExpenseCategory(str, Enum):
		"""
		Types of the user expenses
		"""
		HOUSING = "housing"
		TRANSPORT = "transport"
		FOOD = "food"
		HEALTHCARE = "healthcare"
		INSURANCE = "insurance"
		EDUCATION = "education"
		ENTERTAINMENT = "entertainment"
		DEBT_PAYMENT = "debt_payment"
		INVESTMENT = "investment"
		OTHER = "other"


@dataclass(slots=True)
class Expense(FinancialObject):
		"""
		Expense class of a user
		"""
		id: int
		name: str
		category: ExpenseCategory
		amount: float
		frequency: RecurringFrequency = RecurringFrequency.MONTHLY
		vendor: str = ""
		currency: str = "USD"
		essential: bool = True

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

