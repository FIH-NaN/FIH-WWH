from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Dict, List, Optional

from .liabilities import Liability


class AssetCategory(str, Enum):
	BANK_DEPOSIT = "bank_deposit"
	DIGITAL_ASSET = "digital_asset"
	STOCK = "stock"
	ETF = "etf"
	MUTUAL_FUND = "mutual_fund"
	BOND = "bond"
	REAL_ESTATE = "real_estate"
	COMMODITY = "commodity"
	CASH = "cash"
	OTHER = "other"


@dataclass(slots=True)
class Asset:
	name: str
	category: AssetCategory = field(init=False)
	currency: str = "USD"
	tags: List[str] = field(default_factory=list)

	def current_value(self) -> float:
		raise NotImplementedError("Asset subclasses must implement current_value")

	def is_liquid(self) -> bool:
		return self.category in {
			AssetCategory.BANK_DEPOSIT,
			AssetCategory.CASH,
			AssetCategory.DIGITAL_ASSET,
			AssetCategory.STOCK,
			AssetCategory.ETF,
			AssetCategory.MUTUAL_FUND,
		}


@dataclass(slots=True)
class BankDeposit(Asset):
	institution: str = ""
	account_number_masked: str = ""
	balance: float = 0.0
	annual_interest_rate: float = 0.0

	def __post_init__(self) -> None:
		self.category = AssetCategory.BANK_DEPOSIT

	def current_value(self) -> float:
		return self.balance


@dataclass(slots=True)
class DigitalAsset(Asset):
	symbol: str = ""
	quantity: float = 0.0
	spot_price: float = 0.0
	wallet_address_masked: str = ""

	def __post_init__(self) -> None:
		self.category = AssetCategory.DIGITAL_ASSET

	def current_value(self) -> float:
		return self.quantity * self.spot_price


@dataclass(slots=True)
class Stock(Asset):
	ticker: str = ""
	quantity: float = 0.0
	market_price: float = 0.0
	exchange: str = ""

	def __post_init__(self) -> None:
		self.category = AssetCategory.STOCK

	def current_value(self) -> float:
		return self.quantity * self.market_price


@dataclass(slots=True)
class ETF(Asset):
	ticker: str = ""
	quantity: float = 0.0
	nav_or_market_price: float = 0.0
	expense_ratio: float = 0.0

	def __post_init__(self) -> None:
		self.category = AssetCategory.ETF

	def current_value(self) -> float:
		return self.quantity * self.nav_or_market_price


@dataclass(slots=True)
class Bond(Asset):
	issuer: str = ""
	face_value: float = 0.0
	market_value: float = 0.0
	coupon_rate: float = 0.0
	maturity_date: Optional[date] = None

	def __post_init__(self) -> None:
		self.category = AssetCategory.BOND

	def current_value(self) -> float:
		return self.market_value if self.market_value > 0 else self.face_value


@dataclass(slots=True)
class RealEstate(Asset):
	location: str = ""
	estimated_market_value: float = 0.0
	ownership_share: float = 1.0

	def __post_init__(self) -> None:
		self.category = AssetCategory.REAL_ESTATE

	def current_value(self) -> float:
		return self.estimated_market_value * self.ownership_share

	def is_liquid(self) -> bool:
		return False


@dataclass(slots=True)
class OtherAsset(Asset):
	category: AssetCategory = field(default=AssetCategory.OTHER, init=False)
	amount: float = 0.0
	notes: str = ""

	def current_value(self) -> float:
		return self.amount

