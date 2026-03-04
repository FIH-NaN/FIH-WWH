from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from config import get_settings
from database import init_db
from routers import auth, assets, transactions, categories, scheduler, accounts
from util.scheduler import start_scheduler, shutdown_scheduler
from util.tasks import register_default_tasks

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Initialize database
init_db()

# Startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle app startup and shutdown."""
    # Startup
    start_scheduler()
    register_default_tasks()
    yield
    # Shutdown
    shutdown_scheduler()

# Create FastAPI app
app = FastAPI(
    title=get_settings().API_TITLE,
    version=get_settings().API_VERSION,
    lifespan=lifespan,
)

# Add CORS middleware
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(assets.router)
app.include_router(transactions.router)
app.include_router(categories.router)
app.include_router(scheduler.router)
app.include_router(accounts.router)


@app.get("/")
def root():
    """API root endpoint."""
    return {
        "title": settings.API_TITLE,
        "version": settings.API_VERSION,
        "status": "running",
    }


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
