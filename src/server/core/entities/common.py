from enum import Enum


class RecurringFrequency(str, Enum):
		ONCE = "once"
		WEEKLY = "weekly"
		BIWEEKLY = "biweekly"
		MONTHLY = "monthly"
		QUARTERLY = "quarterly"
		YEARLY = "yearly"

