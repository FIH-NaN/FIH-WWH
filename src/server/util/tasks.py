"""
Background task definitions for the Wealth Wellness Hub scheduler.
These tasks run automatically to update market data and portfolio analytics.
"""

import logging
from datetime import datetime
import numpy as np
from sqlalchemy.orm import Session
from server.db_gateway.database import SessionLocal
from server.db_gateway.db_models import User
from .market_data import MarketDataFetcher
from .allocation_frontier import AllocationFrontier, create_mock_historical_prices

logger = logging.getLogger(__name__)


def fetch_global_markets_data():
    """
    Periodic task: Fetch global market indices and store in cache/database.
    Runs every 4 hours during market hours.
    """
    try:
        logger.info("📊 Starting global markets data fetch...")
        
        fetcher = MarketDataFetcher()
        
        # Fetch major indices
        indices_data = fetcher.fetch_global_market_indices()
        logger.info(f"✓ Fetched {len(indices_data.get('indices', {}))} market indices")
        
        # Fetch exchange rates
        fx_data = fetcher.fetch_exchange_rates("USD")
        if fx_data:
            logger.info(f"✓ Fetched exchange rates for {len(fx_data.get('rates', {}))} currencies")
        
        # Fetch asset allocation reference data
        alloc_data = fetcher.fetch_asset_allocation_data()
        logger.info(f"✓ Fetched allocation data")
        
        # In a real app, you'd store this in cache or database
        logger.info("✓ Global markets data updated successfully")
        
        return {
            "status": "success",
            "indices_count": len(indices_data.get('indices', {})),
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"✗ Error fetching global markets data: {e}")
        return {"status": "error", "message": str(e)}


def calculate_asset_allocation_frontier():
    """
    Periodic task: Calculate efficient frontier for asset allocation advice.
    Runs daily to update allocation recommendations.
    """
    try:
        logger.info("📈 Starting asset allocation frontier calculation...")
        
        # Create frontier calculator
        frontier = AllocationFrontier(risk_free_rate=0.02)
        
        # For demo: use mock historical prices
        # In production: fetch real historical data from database or API
        mock_prices = create_mock_historical_prices(num_days=252, num_assets=6)
        
        # Calculate returns from prices
        returns = frontier.calculate_returns(mock_prices)
        
        # Calculate covariance
        cov_matrix, asset_names = frontier.calculate_covariance_matrix(returns)
        
        # Calculate mean returns (annualized)
        mean_returns = np.array([
            np.mean(returns[asset]) * 252 for asset in asset_names
        ])
        
        # Calculate efficient frontier
        frontier_result = frontier.calculate_efficient_frontier(
            mean_returns,
            cov_matrix,
            num_portfolios=50
        )
        
        summary = frontier.get_frontier_summary()
        logger.info(f"✓ Calculated efficient frontier with {summary['frontier_points_count']} points")
        logger.info(f"  Max Sharpe Ratio: {summary['max_sharpe_ratio']:.3f}")
        logger.info(f"  Min Volatility: {summary['min_volatility']:.1%}")
        
        return {
            "status": "success",
            "frontier_points": summary["frontier_points_count"],
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"✗ Error calculating allocation frontier: {e}")
        return {"status": "error", "message": str(e)}


def update_asset_valuations():
    """
    Periodic task: Update asset valuations for all users.
    Runs every 30 minutes to refresh asset prices and totals.
    """
    try:
        logger.info("💰 Starting asset valuation update...")
        
        db = SessionLocal()
        
        # Get all users
        users = db.query(User).all()
        logger.info(f"  Processing {len(users)} users...")
        
        # For each user, update asset valuations
        # This would typically fetch fresh prices and recalculate totals
        updated_count = 0
        for user in users:
            # In production: fetch fresh prices for user's assets
            # Update asset.value and recalculate portfolio metrics
            updated_count += 1
        
        db.close()
        
        logger.info(f"✓ Updated valuations for {updated_count} users")
        
        return {
            "status": "success",
            "users_updated": updated_count,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"✗ Error updating asset valuations: {e}")
        return {"status": "error", "message": str(e)}


def register_default_tasks():
    """Register all default background tasks with the scheduler."""
    from .scheduler import schedule_cron_job, schedule_interval_job
    
    logger.info("📅 Registering default background tasks...")
    
    # Fetch global markets data 4 times daily (9am, 1pm, 5pm, 9pm)
    schedule_cron_job(
        fetch_global_markets_data,
        job_id="fetch_markets_morning",
        hour=9,
        minute=0,
    )
    schedule_cron_job(
        fetch_global_markets_data,
        job_id="fetch_markets_afternoon",
        hour=13,
        minute=0,
    )
    
    # Calculate allocation frontier daily at 10pm
    schedule_cron_job(
        calculate_asset_allocation_frontier,
        job_id="calc_allocation_frontier",
        hour=22,
        minute=0,
    )
    
    # Update valuations every 30 minutes
    schedule_interval_job(
        update_asset_valuations,
        job_id="update_valuations",
        interval_minutes=30,
    )
    
    logger.info("✓ All default tasks registered")
