from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from src.server.config import get_settings
from src.server.db.database import init_db
from src.server.routers import auth, assets
from src.server.util.scheduler import start_scheduler, shutdown_scheduler
from src.server.util.tasks import register_default_tasks

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Initialize database
init_db()

# Startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle app startup and shutdown."""
    # Startup
    logger.info("Starting up Wealth Wellness Hub API...")
    start_scheduler()
    register_default_tasks()
    logger.info("API startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down API...")
    shutdown_scheduler()
    logger.info("API shutdown complete")

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
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(assets.router)


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
        "src.server.main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
    )
