from typing import Dict, Iterable, Optional

from src.server.core.entities.currency import Currency
import yfinance as yf


def _fetch_rate_to_usd_from_yfinance(currency: Currency) -> Optional[float]:
		"""
		Fetch `currency -> USD` using Yahoo Finance.

		Yahoo symbol format for FX pairs is usually: `XXXUSD=X`.
		"""
		if currency == Currency.USD:
				return 1.0

		pair = f"{currency.value}USD=X"
		try:
				ticker = yf.Ticker(pair)
				hist = ticker.history(period="1d")
				if hist.empty:
						return None
				price = float(hist["Close"].iloc[-1])
				return price if price > 0 else None
		except Exception:
				return None
		

