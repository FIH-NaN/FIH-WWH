from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from typing import Dict, List, Optional, Tuple


class DataSource(str, Enum):
    """Data sources for market information."""
    YAHOO_FINANCE = "yahoo_finance"
    ALPHA_VANTAGE = "alpha_vantage"
    COINMARKETCAP = "coinmarketcap"
    COINGECKO = "coingecko"
    FED = "fed"
    ECB = "ecb"
    MANUAL = "manual"
    CACHE = "cache"


@dataclass(slots=True)
class PricePoint:
    """Single price data point for an asset."""
    date: date
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: Optional[float] = None
    adjusted_close: Optional[float] = None

    def to_dict(self) -> Dict:
        return {
          'date': self.date.isoformat(),
          'open': self.open_price,
          'high': self.high_price,
          'low': self.low_price,
          'close': self.close_price,
          'volume': self.volume,
          'adjusted_close': self.adjusted_close,
        }


@dataclass(slots=True)
class HistoricalPriceData:
	"""Container for historical price data."""
	identifier: str  # ticker, symbol, or asset ID
	prices: List[PricePoint] = field(default_factory=list)
	last_updated: datetime = field(default_factory=datetime.now)
	data_source: DataSource = DataSource.YAHOO_FINANCE

	def add_price_point(self, price_point: PricePoint) -> None:
		"""Add a price point to history."""
		self.prices.append(price_point)
		self.prices.sort(key=lambda p: p.date)
		self.last_updated = datetime.now()

	def get_price_range(self, start_date: date, end_date: date) -> List[PricePoint]:
		"""Get price points within a date range."""
		return [p for p in self.prices if start_date <= p.date <= end_date]

	def get_latest_price(self) -> Optional[float]:
		"""Get the most recent close price."""
		if self.prices:
			return self.prices[-1].close_price
		return None

	def get_returns(self, period_days: int = 1) -> List[float]:
		"""Calculate returns over specified period."""
		if len(self.prices) < period_days + 1:
			return []
		returns = []
		for i in range(period_days, len(self.prices)):
			prev_price = self.prices[i - period_days].close_price
			curr_price = self.prices[i].close_price
			if prev_price > 0:
				ret = (curr_price - prev_price) / prev_price
				returns.append(ret)
		return returns


@dataclass(slots=True)
class Dividend:
    """Dividend payment information."""
    ex_dividend_date: date
    payment_date: date
    dividend_per_share: float
    dividend_yield: Optional[float] = None


  @dataclass(slots=True)
  class StockFundamentals:
    """Stock fundamental metrics for financial analysis."""
    ticker: str
    company_name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    
    # Valuation metrics
    market_cap: Optional[float] = None
    price_to_earnings: Optional[float] = None  # P/E ratio
    price_to_book: Optional[float] = None  # P/B ratio
    price_to_sales: Optional[float] = None  # P/S ratio
    enterprise_value: Optional[float] = None
    
    # Profitability metrics
    earnings_per_share: Optional[float] = None
    book_value_per_share: Optional[float] = None
    revenue_per_share: Optional[float] = None
    net_profit_margin: Optional[float] = None
    return_on_equity: Optional[float] = None  # ROE
    return_on_assets: Optional[float] = None  # ROA
    
    # Growth metrics
    earnings_growth_rate: Optional[float] = None
    revenue_growth_rate: Optional[float] = None
    
    # Dividend information
    annual_dividend_per_share: Optional[float] = None
    dividend_yield: Optional[float] = None
    dividend_payout_ratio: Optional[float] = None
    dividend_history: List[Dividend] = field(default_factory=list)
    
    # Debt metrics
    debt_to_equity: Optional[float] = None
    debt_to_assets: Optional[float] = None
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    
    # Other metrics
    beta: Optional[float] = None  # Volatility relative to market
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None
    
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass(slots=True)
class CryptoFundamentals:
    """Cryptocurrency market data and metrics."""
    symbol: str
    name: str
    
    # Market metrics
    market_cap: Optional[float] = None
    market_cap_rank: Optional[int] = None
    trading_volume_24h: Optional[float] = None
    volume_to_market_cap: Optional[float] = None
    
    # Price metrics
    current_price: Optional[float] = None
    price_change_24h: Optional[float] = None
    price_change_percent_24h: Optional[float] = None
    
    # Supply metrics
    total_supply: Optional[float] = None
    circulating_supply: Optional[float] = None
    max_supply: Optional[float] = None
    
    # Volatility
    price_volatility: Optional[float] = None
    
    # Blockchain info
    blockchain_networks: List[str] = field(default_factory=list)
    contract_addresses: Dict[str, str] = field(default_factory=dict)  # network -> address
    
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass(slots=True)
class ETFFundamentals:
    """ETF-specific market data and characteristics."""
    ticker: str
    fund_name: str
    
    # Fund info
    fund_family: Optional[str] = None
    fund_type: Optional[str] = None  # e.g., "equity", "bond", "commodity"
    investment_strategy: Optional[str] = None
    
    # Asset metrics
    net_asset_value: Optional[float] = None
    total_assets: Optional[float] = None
    shares_outstanding: Optional[float] = None
    
    # Cost metrics
    expense_ratio: Optional[float] = None
    turnover_ratio: Optional[float] = None
    
    # Performance metrics
    one_year_return: Optional[float] = None
    three_year_return: Optional[float] = None
    five_year_return: Optional[float] = None
    ten_year_return: Optional[float] = None
    ytd_return: Optional[float] = None
    
    # Dividend info
    annual_dividend_per_share: Optional[float] = None
    dividend_yield: Optional[float] = None
    
    # Holdings
    top_holdings: Dict[str, float] = field(default_factory=dict)  # symbol -> weight %
    sector_allocation: Dict[str, float] = field(default_factory=dict)  # sector -> weight %
    geographic_allocation: Dict[str, float] = field(default_factory=dict)  # country -> weight %
    
    # Risk metrics
    beta: Optional[float] = None
    standard_deviation: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass(slots=True)
class RealEstateFundamentals:
    """Real estate asset data and valuation metrics."""
    property_id: str
    property_address: str
    
    # Property characteristics
    property_type: Optional[str] = None  # residential, commercial, industrial
    square_footage: Optional[float] = None
    year_built: Optional[int] = None
    
    # Valuation
    estimated_value: Optional[float] = None
    valuation_date: Optional[date] = None
    valuation_method: Optional[str] = None  # "appraised", "assessed", "comparable", "model"
    
    # Income properties
    annual_rental_income: Optional[float] = None
    occupancy_rate: Optional[float] = None  # 0.0 to 1.0
    net_operating_income: Optional[float] = None
    cap_rate: Optional[float] = None  # NOI / property value
    
    # Debt
    outstanding_mortgage: Optional[float] = None
    mortgage_rate: Optional[float] = None
    mortgage_remaining_years: Optional[int] = None
    
    # Metrics
    price_per_sqft: Optional[float] = None
    property_tax_annual: Optional[float] = None
    insurance_annual: Optional[float] = None
    maintenance_reserve_percent: Optional[float] = None
    
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass(slots=True)
class BondFundamentals:
    """Bond and fixed income security data."""
    isin: str  # International Securities Identification Number
    bond_name: str
    issuer: str
    
    # Bond characteristics
    coupon_rate: float
    face_value: float
    maturity_date: date
    current_yield: Optional[float] = None
    yield_to_maturity: Optional[float] = None
    
    # Valuation
    current_price: Optional[float] = None
    credit_rating: Optional[str] = None  # AAA, AA, A, BBB, etc.
    
    # Cash flows
    coupon_frequency_per_year: int = 2  # Usually annual or semi-annual
    next_coupon_date: Optional[date] = None
    
    # Risk metrics
    duration: Optional[float] = None  # Interest rate sensitivity
    modified_duration: Optional[float] = None
    convexity: Optional[float] = None
    option_adjusted_spread: Optional[float] = None
    
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass(slots=True)
class CommodityFundamentals:
    """Commodity market data (metals, energy, agriculture)."""
    symbol: str
    commodity_name: str
    commodity_type: Optional[str] = None  # metal, energy, agriculture
    
    # Price and volume
    spot_price: Optional[float] = None
    price_unit: str = "USD"
    trading_volume: Optional[float] = None
    
    # Fundamentals
    supply_situation: Optional[str] = None
    demand_outlook: Optional[str] = None
    inventory_levels: Optional[float] = None
    
    # Futures contracts (if applicable)
    front_month_contract: Optional[str] = None
    front_month_price: Optional[float] = None
    contango_backwardation: Optional[float] = None
    
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass(slots=True)
class AssetMarketData:
    """Unified asset market data container."""
    asset_id: int
    asset_identifier: str  # ticker, symbol, ISIN, crypto symbol, etc.
    asset_type: str  # stock, etf, bond, crypto, real_estate, commodity
    
    # Historical price data
    price_history: HistoricalPriceData = field(default_factory=lambda: HistoricalPriceData(""))
    
    # Asset-specific fundamentals (only one will be populated)
    stock_fundamentals: Optional[StockFundamentals] = None
    etf_fundamentals: Optional[ETFFundamentals] = None
    crypto_fundamentals: Optional[CryptoFundamentals] = None
    real_estate_fundamentals: Optional[RealEstateFundamentals] = None
    bond_fundamentals: Optional[BondFundamentals] = None
    commodity_fundamentals: Optional[CommodityFundamentals] = None
    
    # Risk/return metrics
    expected_return: Optional[float] = None
    volatility: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    sortino_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    
    # Correlation with market benchmarks
    correlation_with_market: Optional[float] = None
    benchmark_index: Optional[str] = None  # e.g., "SPY", "QQQ"
    
    last_updated: datetime = field(default_factory=datetime.now)
    data_quality_score: float = 0.0  # 0.0 to 1.0, higher is better

    def get_fundamentals(self) -> Optional:
      """Get the populated fundamentals object for this asset."""
      for fundamentals in [
        self.stock_fundamentals,
        self.etf_fundamentals,
        self.crypto_fundamentals,
        self.real_estate_fundamentals,
        self.bond_fundamentals,
        self.commodity_fundamentals,
      ]:
        if fundamentals is not None:
          return fundamentals
      return None

    def get_latest_price(self) -> Optional[float]:
      """Get the most recent price."""
      return self.price_history.get_latest_price()

    def get_annual_volatility(self) -> Optional[float]:
      """Calculate annual volatility from daily returns."""
      daily_returns = self.price_history.get_returns(period_days=1)
      if len(daily_returns) < 2:
        return None
      import statistics
      daily_std = statistics.stdev(daily_returns)
      return daily_std * (252 ** 0.5)  # Annualized: sqrt(252 trading days)
