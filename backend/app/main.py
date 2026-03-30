from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from datetime import datetime
from app.core.config import settings
from app.core.database import test_connection as test_db
from app.services.supabase_client import test_connection as test_supabase

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for resume scoring and bias detection",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    debug=settings.DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Check connections on startup"""
    logger.info("Starting up...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    
    # Test database connection
    if test_db():
        logger.info("Database ready")
    else:
        logger.warning("Database connection failed")
    
    # Test Supabase connection
    if test_supabase():
        logger.info("Supabase ready")
    else:
        logger.warning("Supabase connection failed")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_status = test_db()
    supabase_status = test_supabase()
    
    overall_status = "healthy" if (db_status and supabase_status) else "degraded"
    
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "service": "backend-api",
        "checks": {
            "database": "connected" if db_status else "disconnected",
            "supabase": "connected" if supabase_status else "disconnected"
        }
    }

@app.get("/ready")
async def readiness_check():
    """Readiness probe for orchestration"""
    db_status = test_db()
    
    if db_status:
        return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}
    else:
        return {"status": "not ready", "reason": "database unavailable"}, 503