# Scheduler & Background Tasks Utility

A comprehensive task scheduling system for the Wealth Wellness Hub backend that automatically extracts market information and calculates asset allocation frontiers.

## Architecture

```
util/
├── __init__.py             # Package exports
├── scheduler.py            # APScheduler core & job management
├── market_data.py          # Market data fetching utilities  
├── allocation_frontier.py  # Efficient frontier calculator
└── tasks.py                # Background task definitions
```

## Features

### 1. **Task Scheduling** (`scheduler.py`)

Provides a clean interface around APScheduler for managing background jobs:

- Cron-based scheduling (e.g., daily at 10pm)
- Interval-based scheduling (e.g., every 30 minutes)
- Job management (list, remove, execute)
- Graceful startup/shutdown

**Key Functions:**
```python
from util.scheduler import start_scheduler, schedule_cron_job, schedule_interval_job

# Start scheduler on app startup
start_scheduler()

# Schedule a task to run daily at 10pm
schedule_cron_job(
    job_func=some_task,
    job_id="daily_task",
    hour=22,
    minute=0,
)

# Schedule a task every 30 minutes
schedule_interval_job(
    job_func=another_task,
    job_id="frequent_task",
    interval_minutes=30,
)
```

### 2. **Market Data Fetching** (`market_data.py`)

Fetches real-time and historical market data from public APIs:

- **Stock prices** — Yahoo Finance API
- **Cryptocurrency prices** — CryptoCompare API
- **Exchange rates** — ExchangeRate API
- **Global market indices** — S&P 500, Nasdaq, FTSE, Nikkei, Shanghai, etc.
- **Asset allocation reference data** — Stocks, bonds, commodities, crypto

**Usage:**
```python
from util.market_data import MarketDataFetcher

fetcher = MarketDataFetcher()

# Fetch stock price
stock_data = fetcher.fetch_stock_price("AAPL")

# Fetch crypto price
crypto_data = fetcher.fetch_crypto_price("BTC")

# Fetch exchange rates
fx_data = fetcher.fetch_exchange_rates("USD")

# Fetch global indices
indices = fetcher.fetch_global_market_indices()

# Fetch asset allocation data
alloc_data = fetcher.fetch_asset_allocation_data()
```

### 3. **Efficient Frontier Calculation** (`allocation_frontier.py`)

Implements Modern Portfolio Theory to calculate optimal asset allocations:

- Mean-variance portfolio optimization
- Efficient frontier generation
- Maximum Sharpe Ratio portfolio
- Minimum volatility portfolio
- Covariance matrix calculation
- Risk-return tradeoff visualization data

**Usage:**
```python
from util.allocation_frontier import AllocationFrontier
import numpy as np

# Initialize calculator
frontier = AllocationFrontier(risk_free_rate=0.02)

# Calculate efficient frontier
# Expected returns and covariance matrix from historical data
mean_returns = np.array([0.10, 0.08, 0.12, 0.05])
cov_matrix = np.array([...])  # 4x4 covariance

result = frontier.calculate_efficient_frontier(
    mean_returns=mean_returns,
    cov_matrix=cov_matrix,
    num_portfolios=50  # Generate 50 frontier points
)

# Access optimal portfolios
max_sharpe = result["max_sharpe_portfolio"]
min_vol = result["min_volatility_portfolio"]
frontier_points = result["frontier_points"]
```

### 4. **Scheduled Tasks** (`tasks.py`)

Defines three main background tasks:

#### a. **`fetch_global_markets_data()`**
- Fetches all market indices and exchange rates
- Gathers asset allocation reference data
- Runs: 9am, 1pm daily (configurable)
- Purpose: Keep market data fresh for user reference

#### b. **`calculate_asset_allocation_frontier()`**
- Computes efficient frontier with 50 portfolio points
- Identifies max Sharpe Ratio and min volatility portfolios
- Provides allocation recommendations
- Runs: 10pm daily
- Purpose: Generate daily asset allocation advice

#### c. **`update_asset_valuations()`**
- Updates asset prices for all users
- Recalculates portfolio totals
- Runs: Every 30 minutes
- Purpose: Keep portfolios current

## Integration with FastAPI

The scheduler integrates seamlessly with FastAPI's lifespan events:

```python
from contextlib import asynccontextmanager
from util.scheduler import start_scheduler, shutdown_scheduler
from util.tasks import register_default_tasks

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    start_scheduler()
    register_default_tasks()
    yield
    # Shutdown
    shutdown_scheduler()

app = FastAPI(lifespan=lifespan)
```

## API Endpoints

### View Scheduled Jobs
```
GET /scheduler/jobs?token=YOUR_TOKEN
```

Response:
```json
{
  "success": true,
  "data": {
    "jobs": [
      {
        "id": "fetch_markets_morning",
        "name": "fetch_markets_morning (cron: 9:00)",
        "trigger": "cron[hour='9', minute='0']",
        "next_run_time": "2026-03-05T09:00:00"
      },
      ...
    ],
    "total": 4
  }
}
```

### Manually Trigger a Job
```
POST /scheduler/jobs/{job_id}/trigger?token=YOUR_TOKEN
```

Example:
```bash
curl -X POST \
  "http://localhost:8000/scheduler/jobs/calc_allocation_frontier/trigger?token=YOUR_TOKEN"
```

### View Scheduler Status
```
GET /scheduler/status?token=YOUR_TOKEN
```

Response:
```json
{
  "success": true,
  "data": {
    "running": true,
    "jobs_count": 4,
    "jobs": [...]
  }
}
```

### Remove a Job
```
DELETE /scheduler/jobs/{job_id}?token=YOUR_TOKEN
```

## Default Schedule

| Task | Trigger | Frequency | Purpose |
|------|---------|-----------|---------|
| `fetch_markets_morning` | 9:00 AM | Daily | Morning market data fetch |
| `fetch_markets_afternoon` | 1:00 PM | Daily | Afternoon market data fetch |
| `calc_allocation_frontier` | 10:00 PM | Daily | Calculate efficient frontier |
| `update_valuations` | Every 30 min | Every 30 minutes | Update user asset prices |

## Performance Considerations

### Market Data Fetching
- Uses public APIs with rate limiting (no auth keys needed)
- Average response time: 2-3 seconds
- Can be cached to reduce API calls
- Handles API failures gracefully with logging

### Efficient Frontier Calculation
- Computation time: ~100-500ms depending on portfolio size
- Uses scipy optimization (SLSQP algorithm)
- Generates 50 frontier points per calculation
- Memory efficient with numpy arrays

### Valuation Updates
- Runs every 30 minutes for all users
- Queries database once for all users
- Batch operation: O(n) where n = number of assets
- Can be parallelized per user

## Example: Adding Custom Tasks

```python
from util.scheduler import schedule_cron_job, schedule_interval_job

def my_custom_task(param1: str, param2: int = 10):
    """Your custom background task."""
    logger.info(f"Running custom task: {param1}")
    # Do something useful...
    return {"status": "success"}

# Schedule it
schedule_cron_job(
    my_custom_task,
    job_id="my_custom_daily",
    hour=15,  # 3 PM
    minute=30,
    replace_existing=True,
    # Pass kwargs to the function
    param1="important_data",
    param2=20,
)
```

## Logging

All scheduler activities are logged with appropriate levels:

```
INFO  - ✓ Background task scheduler started
INFO  - ✓ Scheduled cron job: fetch_markets_morning at 9:00
INFO  - 📊 Starting global markets data fetch...
INFO  - ✓ Fetched 6 market indices
INFO  - ✓ Global markets data updated successfully
ERROR - ✗ Error fetching global markets data: Connection timeout
```

Monitor logs for task execution:
```bash
# Watch logs (if running with uvicorn)
tail -f server.log | grep scheduler
```

## Testing Tasks Manually

```python
# In Python REPL or test file
from util.tasks import (
    fetch_global_markets_data,
    calculate_asset_allocation_frontier,
    update_asset_valuations,
)

# Run a task manually
result = fetch_global_markets_data()
print(result)

# Output:
# {
#   'status': 'success',
#   'indices_count': 6,
#   'timestamp': '2026-03-04T15:30:00'
# }
```

## Future Enhancements

- [ ] Database caching for market data
- [ ] Redis support for distributed scheduling
- [ ] Task retries with exponential backoff
- [ ] Email/webhook notifications on task failure
- [ ] Custom user-defined task scheduling
- [ ] Task execution history & metrics
- [ ] WebSocket live updates during task execution
- [ ] Integration with external data providers (Alpha Vantage, IEX Cloud)

## Troubleshooting

### Scheduler not starting
- Check logs for startup errors
- Ensure APScheduler is installed: `pip install apscheduler`
- Verify database connection

### Tasks not running
- Verify scheduler is in running state (check `/scheduler/status`)
- Check system time and timezone
- Review task function errors in logs

### API errors
- Ensure token is valid and not expired
- Check user exists in database
- Verify scheduler.py router is included in main.py

## References

- [APScheduler Documentation](https://apscheduler.readthedocs.io/)
- [Modern Portfolio Theory (Wikipedia)](https://en.wikipedia.org/wiki/Modern_portfolio_theory)
- [Efficient Frontier](https://en.wikipedia.org/wiki/Efficient_frontier)
