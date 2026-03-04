"""
Market data fetching utilities for real-time and historical data.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import requests

logger = logging.getLogger(__name__)


class MarketDataFetcher:
    """Fetches market data from public APIs."""

    # Public APIs (no auth required)
    YFINANCE_URL = "https://query1.finance.yahoo.com/v7/finance/quote"
    CRYPTO_COMPARE_URL = "https://min-api.cryptocompare.com/data/price"
    EX_RATE_URL = "https://api.exchangerate-api.com/v4/latest"

    @staticmethod
    def fetch_stock_price(ticker: str) -> Optional[Dict]:
        """
        Fetch current stock price from Yahoo Finance API.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')
            
        Returns:
            Dict with price data or None if failed
        """
        try:
            params = {"symbols": ticker}
            response = requests.get(
                MarketDataFetcher.YFINANCE_URL,
                params=params,
                timeout=5,
            )
            response.raise_for_status()
            data = response.json()

            if "quoteResponse" in data and data["quoteResponse"]["result"]:
                quote = data["quoteResponse"]["result"][0]
                return {
                    "ticker": ticker,
                    "price": quote.get("regularMarketPrice"),
                    "currency": quote.get("currency", "USD"),
                    "timestamp": datetime.utcnow().isoformat(),
                    "change_percent": quote.get("regularMarketChangePercent"),
                }
        except Exception as e:
            logger.error(f"Failed to fetch stock price for {ticker}: {e}")

        return None

    @staticmethod
    def fetch_crypto_price(symbol: str, vs_currency: str = "USD") -> Optional[Dict]:
        """
        Fetch current cryptocurrency price.
        
        Args:
            symbol: Crypto symbol (e.g., 'BTC', 'ETH')
            vs_currency: Target currency (default: USD)
            
        Returns:
            Dict with price data or None if failed
        """
        try:
            params = {
                "fsym": symbol.upper(),
                "tsyms": vs_currency.upper(),
            }
            response = requests.get(
                MarketDataFetcher.CRYPTO_COMPARE_URL,
                params=params,
                timeout=5,
            )
            response.raise_for_status()
            data = response.json()

            if vs_currency.upper() in data:
                return {
                    "symbol": symbol.upper(),
                    "price": data[vs_currency.upper()],
                    "currency": vs_currency.upper(),
                    "timestamp": datetime.utcnow().isoformat(),
                }
        except Exception as e:
            logger.error(f"Failed to fetch crypto price for {symbol}: {e}")

        return None

    @staticmethod
    def fetch_exchange_rates(base_currency: str = "USD") -> Optional[Dict]:
        """
        Fetch current exchange rates.
        
        Args:
            base_currency: Base currency for rates
            
        Returns:
            Dict with exchange rates or None if failed
        """
        try:
            response = requests.get(
                f"{MarketDataFetcher.EX_RATE_URL}/{base_currency.upper()}",
                timeout=5,
            )
            response.raise_for_status()
            data = response.json()

            return {
                "base": data.get("base"),
                "rates": data.get("rates", {}),
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to fetch exchange rates for {base_currency}: {e}")

        return None

    @staticmethod
    def fetch_global_market_indices() -> Dict:
        """
        Fetch major global market indices.
        Common indices: ^GSPC (S&P 500), ^IXIC (Nasdaq), ^FTSE (FTSE 100), etc.
        
        Returns:
            Dict with multiple index data
        """
        indices = {
            "^GSPC": "S&P 500",      # US Large Cap
            "^IXIC": "Nasdaq-100",   # US Tech
            "^FTSE": "FTSE 100",     # UK
            "^N225": "Nikkei 225",   # Japan
            "^SSEC": "Shanghai Index", # China
            "^AORD": "ASX 200",      # Australia
        }

        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "indices": {},
        }

        for ticker, name in indices.items():
            data = MarketDataFetcher.fetch_stock_price(ticker)
            if data:
                results["indices"][name] = data

        return results

    @staticmethod
    def fetch_asset_allocation_data() -> Dict:
        """
        Fetch representative assets for global allocation analysis.
        Includes stocks, bonds, commodities, and crypto benchmarks.
        
        Returns:
            Dict with asset class data for frontier calculation
        """
        assets = {
            "stocks": {
                "us": "^GSPC",        # S&P 500
                "international": "^STOXX50E",  # European blue chips
                "emerging": "^BVSP",  # Brazil (EM proxy)
            },
            "fixed_income": {
                "us_10y": "^TNX",     # US 10Y Yield
                "us_corporate": "^OEX",  # S&P 100 (defensive)
            },
            "commodities": {
                "gold": "GC=F",       # Gold futures
                "oil": "CL=F",        # WTI Oil futures
            },
            "crypto": {
                "bitcoin": "BTC",
                "ethereum": "ETH",
            },
        }

        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "allocation_data": {}
        }

        # Fetch stocks
        for category, tickers_dict in assets.items():
            results["allocation_data"][category] = {}
            for asset_name, ticker in tickers_dict.items():
                if category == "crypto":
                    data = MarketDataFetcher.fetch_crypto_price(ticker)
                else:
                    data = MarketDataFetcher.fetch_stock_price(ticker)

                if data:
                    results["allocation_data"][category][asset_name] = data

        return results
