"""
Task scheduler utilities for Wealth Wellness Hub.
Handles scheduling of background tasks like market data extraction and portfolio optimization.
"""

from .scheduler import get_scheduler
from .tasks import (
    fetch_global_markets_data,
    calculate_asset_allocation_frontier,
    update_asset_valuations,
)

__all__ = [
    "get_scheduler",
    "fetch_global_markets_data",
    "calculate_asset_allocation_frontier",
    "update_asset_valuations",
]
