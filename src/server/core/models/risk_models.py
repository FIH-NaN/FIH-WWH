from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
import statistics


@dataclass(slots=True)
class GarchModel:
	"""
	GARCH (Generalized Autoregressive Conditional Heteroskedasticity) model
	for volatility forecasting.
	"""
	asset_id: int
	asset_identifier: str
	
	# Model parameters
	p: int = 1  # AR order
	q: int = 1  # MA order
	
	# Coefficients
	omega: float = 0.0  # Long-run average variance
	alpha: List[float] = field(default_factory=list)  # Alpha coefficients (length p)
	beta: List[float] = field(default_factory=list)   # Beta coefficients (length q)
	
	# Historical data
	returns: List[float] = field(default_factory=list)
	variances: List[float] = field(default_factory=list)  # Conditional variances
	
	# Forecasts
	forecasted_variances: List[float] = field(default_factory=list)
	forecast_horizon: int = 20  # Number of periods to forecast
	
	# Model performance
	log_likelihood: Optional[float] = None
	aic: Optional[float] = None  # Akaike Information Criterion
	bic: Optional[float] = None  # Bayesian Information Criterion
	
	last_updated: datetime = field(default_factory=datetime.now)
	fitted: bool = False

	def calculate_conditional_variance(self, index: int) -> float:
		"""Calculate conditional variance at specified index."""
		if index == 0:
			return self.omega
		
		variance = self.omega
		
		# Add alpha terms (ARCH terms)
		for i in range(self.p):
			if index - i - 1 >= 0 and index - i - 1 < len(self.returns):
				variance += self.alpha[i] * (self.returns[index - i - 1] ** 2)
		
		# Add beta terms (GARCH terms)
		for i in range(self.q):
			if index - i - 1 >= 0 and index - i - 1 < len(self.variances):
				variance += self.beta[i] * self.variances[index - i - 1]
		
		return max(variance, 0.0)  # Variance cannot be negative

	def forecast_volatility(self) -> List[float]:
		"""Forecast future volatilities."""
		if not self.fitted or not self.variances:
			return []
		
		forecasts = []
		last_variance = self.variances[-1]
		
		for h in range(self.forecast_horizon):
			# Long-run variance is omega / (1 - sum(alpha) - sum(beta))
			alpha_sum = sum(self.alpha) if self.alpha else 0
			beta_sum = sum(self.beta) if self.beta else 0
			denominator = 1 - alpha_sum - beta_sum
			
			if denominator > 0:
				long_run_var = self.omega / denominator
			else:
				long_run_var = last_variance
			
			# Multi-step ahead forecast converges to long-run variance
			forecast_var = long_run_var
			forecasts.append(forecast_var ** 0.5)  # Convert variance to volatility
		
		return forecasts


@dataclass(slots=True)
class ValueAtRisk:
	"""Value at Risk (VaR) models for portfolio risk assessment."""
	asset_id: int
	asset_identifier: str
	
	# VaR parameters
	confidence_level: float = 0.95  # 95% confidence (5% tail risk)
	time_horizon_days: int = 1  # 1-day VaR by default
	
	# Historical data for calculation
	returns: List[float] = field(default_factory=list)
	
	# VaR estimates using different methods
	var_historical: Optional[float] = None  # Historical simulation
	var_parametric: Optional[float] = None  # Assume normal distribution
	var_cornish_fisher: Optional[float] = None  # Accounts for skewness and kurtosis
	
	# CVaR (Conditional Value at Risk / Expected Shortfall)
	cvar: Optional[float] = None
	
	# Value at Risk for different time horizons
	var_10day: Optional[float] = None
	var_30day: Optional[float] = None
	
	# Parametric assumptions
	mean_return: Optional[float] = None
	volatility: Optional[float] = None
	skewness: Optional[float] = None
	kurtosis: Optional[float] = None
	
	last_updated: datetime = field(default_factory=datetime.now)

	def calculate_parametric_var(self) -> float:
		"""Calculate VaR assuming normal distribution."""
		if self.mean_return is None or self.volatility is None:
			return 0.0
		
		# Z-score for confidence level (for 95% confidence, Z ≈ 1.645)
		z_scores = {0.90: 1.282, 0.95: 1.645, 0.99: 2.326}
		z = z_scores.get(self.confidence_level, 1.645)
		
		# VaR = mean - volatility * z-score
		var = self.mean_return - self.volatility * z
		return var

	def calculate_historical_var(self) -> float:
		"""Calculate VaR using historical simulation."""
		if not self.returns:
			return 0.0
		
		sorted_returns = sorted(self.returns)
		index = int(len(sorted_returns) * (1 - self.confidence_level))
		return sorted_returns[index]


@dataclass(slots=True)
class CovarianceMatrix:
	"""Covariance matrix for portfolio assets."""
	asset_ids: List[int] = field(default_factory=list)
	asset_identifiers: List[str] = field(default_factory=list)
	
	# Covariance matrix (stored as dict for flexibility)
	data: Dict[Tuple[int, int], float] = field(default_factory=dict)
	
	# Correlation matrix (for reference)
	correlation_data: Dict[Tuple[int, int], float] = field(default_factory=dict)
	
	last_updated: datetime = field(default_factory=datetime.now)

	def set_covariance(self, asset_i_id: int, asset_j_id: int, cov: float) -> None:
		"""Set covariance between two assets."""
		self.data[(asset_i_id, asset_j_id)] = cov
		self.data[(asset_j_id, asset_i_id)] = cov

	def get_covariance(self, asset_i_id: int, asset_j_id: int) -> float:
		"""Get covariance between two assets."""
		return self.data.get((asset_i_id, asset_j_id), 0.0)

	def set_correlation(self, asset_i_id: int, asset_j_id: int, corr: float) -> None:
		"""Set correlation between two assets."""
		self.correlation_data[(asset_i_id, asset_j_id)] = corr
		self.correlation_data[(asset_j_id, asset_i_id)] = corr

	def get_correlation(self, asset_i_id: int, asset_j_id: int) -> float:
		"""Get correlation between two assets."""
		return self.correlation_data.get((asset_i_id, asset_j_id), 0.0)

	def to_numpy_array(self) -> Optional:
		"""Convert to numpy array if numpy is available."""
		try:
			import numpy as np
			n = len(self.asset_ids)
			matrix = np.zeros((n, n))
			for i, aid_i in enumerate(self.asset_ids):
				for j, aid_j in enumerate(self.asset_ids):
					matrix[i, j] = self.get_covariance(aid_i, aid_j)
			return matrix
		except ImportError:
			return None


@dataclass(slots=True)
class CorrelationMatrix:
	"""Asset correlation matrix for diversification analysis."""
	asset_ids: List[int] = field(default_factory=list)
	asset_identifiers: List[str] = field(default_factory=list)
	
	# Correlation data (stored as dict)
	data: Dict[Tuple[int, int], float] = field(default_factory=dict)
	
	last_updated: datetime = field(default_factory=datetime.now)

	def set_correlation(self, asset_i_id: int, asset_j_id: int, corr: float) -> None:
		"""Set correlation between two assets (should be between -1 and 1)."""
		corr = max(-1.0, min(1.0, corr))  # Clamp to [-1, 1]
		self.data[(asset_i_id, asset_j_id)] = corr
		self.data[(asset_j_id, asset_i_id)] = corr

	def get_correlation(self, asset_i_id: int, asset_j_id: int) -> float:
		"""Get correlation between two assets."""
		if asset_i_id == asset_j_id:
			return 1.0
		return self.data.get((asset_i_id, asset_j_id), 0.0)

	def get_average_correlation(self) -> float:
		"""Get average correlation across all asset pairs."""
		if len(self.data) == 0:
			return 0.0
		# Exclude self-correlations
		correlations = [v for k, v in self.data.items() if k[0] != k[1]]
		if not correlations:
			return 0.0
		return sum(correlations) / len(correlations)


@dataclass(slots=True)
class EfficientFrontier:
	"""Efficient frontier for optimal portfolio allocation."""
	asset_ids: List[int] = field(default_factory=list)
	
	# Frontier data: list of (return, volatility) tuples
	frontier_points: List[Tuple[float, float]] = field(default_factory=list)
	
	# Optimal portfolios
	min_volatility_weights: Dict[int, float] = field(default_factory=dict)  # MVP weights
	max_sharpe_weights: Dict[int, float] = field(default_factory=dict)  # Max Sharpe weights
	
	# Inputs
	expected_returns: Dict[int, float] = field(default_factory=dict)
	volatilities: Dict[int, float] = field(default_factory=dict)
	covariance_matrix: Optional[CovarianceMatrix] = None
	
	# Risk-free rate
	risk_free_rate: float = 0.02  # 2% default
	
	# Performance metrics
	min_volatility_portfolio_return: Optional[float] = None
	min_volatility_portfolio_volatility: Optional[float] = None
	min_volatility_portfolio_sharpe: Optional[float] = None
	
	max_sharpe_portfolio_return: Optional[float] = None
	max_sharpe_portfolio_volatility: Optional[float] = None
	max_sharpe_portfolio_sharpe: Optional[float] = None
	
	last_updated: datetime = field(default_factory=datetime.now)


@dataclass(slots=True)
class BetaCalculation:
	"""Beta calculations for assets relative to market benchmark."""
	asset_id: int
	asset_identifier: str
	benchmark_identifier: str  # e.g., "SPY" for S&P 500
	
	# Beta value
	beta: Optional[float] = None
	
	# Calculation method
	method: str = "regression"  # "regression" or "covariance"
	period_days: int = 252  # One year of trading days
	
	# Supporting data
	asset_returns: List[float] = field(default_factory=list)
	benchmark_returns: List[float] = field(default_factory=list)
	
	# Regression statistics
	r_squared: Optional[float] = None
	alpha: Optional[float] = None
	correlation: Optional[float] = None
	
	last_updated: datetime = field(default_factory=datetime.now)

	def interpret_beta(self) -> str:
		"""Interpret beta value."""
		if self.beta is None:
			return "Unknown"
		if self.beta < 0.8:
			return "Defensive (less volatile than market)"
		elif self.beta < 1.2:
			return "In-line (similar volatility to market)"
		else:
			return "Aggressive (more volatile than market)"


def calc_sharpe_ratio(r: float, rf: float, sd: float):
		# todo
		pass

def calc_sortino_ratio():
		# todo
		pass


def calc_max_drawdown(prices):
		pass
		# todo
