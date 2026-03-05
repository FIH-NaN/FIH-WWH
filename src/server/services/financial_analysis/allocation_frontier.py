"""
Asset allocation frontier calculation using Modern Portfolio Theory.
Computes efficient frontier and optimal portfolios.
"""

import logging
from typing import Dict, List, Tuple, Optional
import numpy as np
from scipy.optimize import minimize
from datetime import datetime

logger = logging.getLogger(__name__)


class AllocationFrontier:
    """
    Efficient Frontier Calculator using Mean-Variance Optimization.
    Applies Modern Portfolio Theory to compute optimal asset allocations.
    """

    def __init__(self, risk_free_rate: float = 0.02):
        """
        Initialize frontier calculator.
        
        Args:
            risk_free_rate: Annual risk-free rate (default 2%)
        """
        self.risk_free_rate = risk_free_rate
        self.last_calculation = None
        self.frontier_data = None

    def calculate_returns(self, prices: Dict[str, List[float]]) -> Dict[str, List[float]]:
        """
        Calculate daily returns from price series.
        
        Args:
            prices: Dict mapping asset names to price history lists
            
        Returns:
            Dict mapping asset names to daily return lists
        """
        returns = {}
        for asset, price_list in prices.items():
            if len(price_list) < 2:
                continue
            # Calculate percentage returns
            price_array = np.array(price_list)
            daily_returns = np.diff(price_array) / price_array[:-1]
            returns[asset] = daily_returns.tolist()
        return returns

    def calculate_covariance_matrix(self, returns: Dict[str, List[float]]) -> Tuple[np.ndarray, List[str]]:
        """
        Calculate covariance matrix from returns.
        
        Args:
            returns: Dict mapping asset names to return lists
            
        Returns:
            Tuple of (covariance matrix, asset names in order)
        """
        asset_names = sorted(returns.keys())
        return_arrays = [np.array(returns[asset]) for asset in asset_names]
        
        # Stack returns and calculate covariance
        returns_matrix = np.column_stack(return_arrays)
        cov_matrix = np.cov(returns_matrix.T)
        
        # Annualize covariance (assuming daily data, 252 trading days/year)
        cov_matrix_annual = cov_matrix * 252
        
        return cov_matrix_annual, asset_names

    def expected_return(self, weights: np.ndarray, returns: Dict[str, float]) -> float:
        """Calculate portfolio expected return."""
        asset_names = sorted(returns.keys())
        mean_returns = np.array([returns[asset] for asset in asset_names])
        return np.sum(mean_returns * weights)

    def portfolio_volatility(
        self,
        weights: np.ndarray,
        cov_matrix: np.ndarray
    ) -> float:
        """Calculate portfolio volatility (standard deviation)."""
        return np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))

    def negative_sharpe_ratio(
        self,
        weights: np.ndarray,
        mean_returns: np.ndarray,
        cov_matrix: np.ndarray,
        risk_free_rate: float = 0.02
    ) -> float:
        """Calculate negative Sharpe ratio (for minimization)."""
        p_return = np.sum(mean_returns * weights)
        p_volatility = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
        return -(p_return - risk_free_rate) / p_volatility if p_volatility > 0 else 0

    def find_maximum_sharpe_ratio_portfolio(
        self,
        mean_returns: np.ndarray,
        cov_matrix: np.ndarray,
        num_assets: int
    ) -> Tuple[np.ndarray, float, float]:
        """
        Find portfolio weights that maximize Sharpe ratio.
        
        Returns:
            Tuple of (weights, return, volatility)
        """
        constraints = ({"type": "eq", "fun": lambda w: np.sum(w) - 1})
        bounds = tuple((0, 1) for _ in range(num_assets))
        initial_weights = np.array([1.0 / num_assets] * num_assets)

        result = minimize(
            self.negative_sharpe_ratio,
            initial_weights,
            args=(mean_returns, cov_matrix, self.risk_free_rate),
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
        )

        optimal_weights = result.x
        optimal_return = np.sum(mean_returns * optimal_weights)
        optimal_volatility = np.sqrt(
            np.dot(optimal_weights, np.dot(cov_matrix, optimal_weights))
        )

        return optimal_weights, optimal_return, optimal_volatility

    def find_minimum_volatility_portfolio(
        self,
        cov_matrix: np.ndarray,
        num_assets: int
    ) -> Tuple[np.ndarray, float]:
        """
        Find portfolio weights that minimize volatility.
        
        Returns:
            Tuple of (weights, volatility)
        """
        constraints = ({"type": "eq", "fun": lambda w: np.sum(w) - 1})
        bounds = tuple((0, 1) for _ in range(num_assets))
        initial_weights = np.array([1.0 / num_assets] * num_assets)

        result = minimize(
            lambda w: self.portfolio_volatility(w, cov_matrix),
            initial_weights,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
        )

        optimal_weights = result.x
        optimal_volatility = np.sqrt(
            np.dot(optimal_weights, np.dot(cov_matrix, optimal_weights))
        )

        return optimal_weights, optimal_volatility

    def calculate_efficient_frontier(
        self,
        mean_returns: np.ndarray,
        cov_matrix: np.ndarray,
        num_portfolios: int = 50
    ) -> Dict:
        """
        Calculate efficient frontier with multiple portfolio points.
        
        Args:
            mean_returns: Array of expected returns for each asset
            cov_matrix: Covariance matrix of asset returns
            num_portfolios: Number of points along frontier
            
        Returns:
            Dict with frontier points, optimal portfolios, etc.
        """
        num_assets = len(mean_returns)
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "frontier_points": [],
            "max_sharpe_portfolio": None,
            "min_volatility_portfolio": None,
        }

        # Find maximum Sharpe ratio portfolio
        max_sharpe_weights, max_sharpe_return, max_sharpe_vol = \
            self.find_maximum_sharpe_ratio_portfolio(mean_returns, cov_matrix, num_assets)

        results["max_sharpe_portfolio"] = {
            "weights": max_sharpe_weights.tolist(),
            "expected_return": float(max_sharpe_return),
            "volatility": float(max_sharpe_vol),
            "sharpe_ratio": float((max_sharpe_return - self.risk_free_rate) / max_sharpe_vol),
        }

        # Find minimum volatility portfolio
        min_vol_weights, min_vol = \
            self.find_minimum_volatility_portfolio(cov_matrix, num_assets)

        results["min_volatility_portfolio"] = {
            "weights": min_vol_weights.tolist(),
            "expected_return": float(np.sum(mean_returns * min_vol_weights)),
            "volatility": float(min_vol),
            "sharpe_ratio": float((np.sum(mean_returns * min_vol_weights) - self.risk_free_rate) / min_vol),
        }

        # Generate efficient frontier points
        min_return = min_vol_weights @ mean_returns
        max_return = max(mean_returns)
        target_returns = np.linspace(min_return, max_return, num_portfolios)

        for target_return in target_returns:
            constraints = (
                {"type": "eq", "fun": lambda w: np.sum(w) - 1},
                {"type": "eq", "fun": lambda w: w @ mean_returns - target_return},
            )
            bounds = tuple((0, 1) for _ in range(num_assets))
            initial_weights = np.array([1.0 / num_assets] * num_assets)

            result = minimize(
                lambda w: self.portfolio_volatility(w, cov_matrix),
                initial_weights,
                method="SLSQP",
                bounds=bounds,
                constraints=constraints,
            )

            if result.success:
                portfolio_vol = self.portfolio_volatility(result.x, cov_matrix)
                results["frontier_points"].append({
                    "return": float(target_return),
                    "volatility": float(portfolio_vol),
                    "weights": result.x.tolist(),
                })

        self.last_calculation = datetime.utcnow()
        self.frontier_data = results
        logger.info(f"✓ Calculated efficient frontier with {len(results['frontier_points'])} points")

        return results

    def get_frontier_summary(self) -> Dict:
        """Get summary of last frontier calculation."""
        if not self.frontier_data:
            return {"status": "No frontier calculated yet"}

        return {
            "calculated_at": self.last_calculation.isoformat(),
            "max_sharpe_ratio": self.frontier_data["max_sharpe_portfolio"]["sharpe_ratio"],
            "max_sharpe_return": self.frontier_data["max_sharpe_portfolio"]["expected_return"],
            "max_sharpe_volatility": self.frontier_data["max_sharpe_portfolio"]["volatility"],
            "min_volatility": self.frontier_data["min_volatility_portfolio"]["volatility"],
            "frontier_points_count": len(self.frontier_data["frontier_points"]),
        }


def create_mock_historical_prices(num_days: int = 252, num_assets: int = 6) -> Dict[str, List[float]]:
    """
    Create mock historical prices for testing.
    
    Args:
        num_days: Number of trading days to simulate
        num_assets: Number of asset classes
        
    Returns:
        Dict mapping asset names to price histories
    """
    np.random.seed(42)  # For reproducibility
    
    asset_names = [
        "US_Stocks",
        "International_Stocks",
        "Bonds",
        "Real_Estate",
        "Commodities",
        "Crypto"
    ]
    
    prices = {}
    for i, asset in enumerate(asset_names[:num_assets]):
        # Generate random walk prices
        returns = np.random.normal(0.0005, 0.015, num_days)  # Daily return distribution
        price = 100 * np.exp(np.cumsum(returns))
        prices[asset] = price.tolist()
    
    return prices
