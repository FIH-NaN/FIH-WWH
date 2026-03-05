from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from src.server.core.entities.financials.assets import Asset, AssetCategory
from src.server.core.entities.financials.liabilities import Liability


@dataclass(slots=True)
class Portfolio:
    """
    A user's complete portfolio containing all their assets, liabilities.
    """
    user_id: int
    assets: Dict[int, Asset]
    liabilities: Dict[int, Liability]

    init_timestamp: datetime
    last_update_timestamp: datetime
    
    def get_portfolio_returns(self):
        pass
    
    def get_portfolio_standard_deviations(self):
        pass
    
    def get_sharpe(self):
        pass
    
