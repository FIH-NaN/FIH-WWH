from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Iterable, Optional

from src.server.core.entities.currency import Currency
from server.services.data_fetcher.requests import _fetch_rate_to_usd_from_yfinance


# exchange rate based on usd
exchange_rates_benchmark: Dict[Currency, float] = {
		Currency.USD: 1.0,
		Currency.EUR: 1.09,
		Currency.GBP: 1.27,
		Currency.JPY: 0.0067,
		Currency.CNY: 0.14,
		Currency.HKD: 0.128,
		Currency.SGD: 0.74,
		Currency.AUD: 0.66,
		Currency.CAD: 0.73,
		Currency.CHF: 1.12,
		Currency.NZD: 0.61,
		Currency.SEK: 0.095,
		Currency.NOK: 0.093,
		Currency.DKK: 0.146,
		Currency.INR: 0.012,
}


def get_exchange_rates_benchmark() -> Dict[Currency, float]:
		"""Return a copy of current default exchange rates to USD."""
		return dict(exchange_rates_benchmark)


@dataclass(slots=True)
class CurrencyMarketData:
		"""
		Maintains currency exchange rates (to USD) and refreshes from market data.
		"""

		last_updated: Optional[datetime] = None
		exchange_rate_to_usd: Dict[Currency, float] = field(
				default_factory=lambda: dict(exchange_rates_benchmark)
		)

		def get_rate_to_usd(self, currency: Currency) -> float:
				"""Get exchange rate from currency to USD."""
				return self.exchange_rate_to_usd.get(currency, 1.0 if currency == Currency.USD else 0.0)

		def convert(self, amount: float, source: Currency, target: Currency) -> float:
				"""
				Convert amount from source currency to target currency using USD cross rates.
				"""
				source_to_usd = self.get_rate_to_usd(source)
				target_to_usd = self.get_rate_to_usd(target)
				if source_to_usd <= 0 or target_to_usd <= 0:
						raise ValueError("Unsupported exchange rate for conversion")
				usd_amount = amount * source_to_usd
				return usd_amount / target_to_usd

		def update(self) -> None:
				"""
				Retrieve market data for exchange rates and update the local dict.
				"""
				updated: Dict[Currency, float] = {}
				
				for curr in list(Currency):
						live_rate = _fetch_rate_to_usd_from_yfinance(curr)
						if live_rate is not None and live_rate > 0:
								updated[curr] = live_rate
						else:
								updated[curr] = self.exchange_rate_to_usd.get(
										curr,
										exchange_rates_benchmark.get(curr, 1.0 if curr == Currency.USD else 0.0),
								)

				self.exchange_rate_to_usd.update(updated)
				self.last_updated = datetime.now()

		def retrieve_currency_data(
				self,
				currencies: Optional[Iterable[Currency]] = None,
				force_refresh: bool = False,
		) -> Dict[Currency, float]:
				"""
				Retrieve currency exchange rates based on usd.
				
				Args:
						currencies: Specific currencies to retrieve. If None, returns all.
						force_refresh: If True, fetches fresh data from market before returning.
				
				Returns:
						Dictionary of currency exchange rates to USD.
				"""
				if force_refresh:
						self.update()
				
				if currencies is None:
						return dict(self.exchange_rate_to_usd)
				
				result: Dict[Currency, float] = {}
				for curr in currencies:
						result[curr] = self.get_rate_to_usd(curr)
				
				return result
