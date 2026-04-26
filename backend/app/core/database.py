from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator, Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Lazy initialization cache
_engine_cache: Optional[object] = None

def _create_engine():
    if not settings.DATABASE_URL:
        logger.error("DATABASE_URL is not set - database will not be available")
        return None
    try:
        return create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,  # Verify connections before using
            pool_recycle=3600,   # Recycle connections after 1 hour
            pool_size=10,        # Number of connections to keep in pool
            max_overflow=20,     # Maximum overflow connections
            echo=settings.DEBUG,  # Log SQL queries in debug mode
            connect_args={
                "connect_timeout": 5,  # 5 second timeout on initial connection
                "application_name": "trustlens-backend",
            },
        )
    except Exception as e:
        logger.error("Failed to create database engine: %s", str(e))
        return None


def get_engine() -> Optional[object]:
    """Get or create database engine (lazy initialization)"""
    global _engine_cache
    if _engine_cache is None and settings.DATABASE_URL:
        _engine_cache = _create_engine()
    return _engine_cache


# Lazy property for backward compatibility with code that imports 'engine'
class LazyEngine:
    """Lazy wrapper for database engine that defers creation until first access"""
    def __getattr__(self, name):
        engine = get_engine()
        if engine is None:
            raise RuntimeError("Database is not configured or unreachable")
        return getattr(engine, name)

# Create lazy engine instance for backward compatibility
engine = LazyEngine()

def _require_engine():
    current_engine = get_engine()
    if current_engine is None:
        raise RuntimeError("Database is not configured or unreachable (engine not initialized)")
    return current_engine

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False)

# Base class for models
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session"""
    current_engine = get_engine()
    if current_engine is None:
        raise RuntimeError("Database is not configured or unreachable")
    
    # Configure session with engine if not already done
    SessionLocal.configure(bind=current_engine)
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_database_connection() -> bool:
    """Test database connection"""
    try:
        current_engine = get_engine()
        if current_engine is None:
            logger.error("Database not configured")
            return False
        
        SessionLocal.configure(bind=current_engine)
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False

def init_database():
    """Initialize database (create tables if not exist)"""
    from app.models import candidate, score, bias_metric, feedback
    
    try:
        current_engine = get_engine()
        if current_engine is None:
            raise RuntimeError("Database is not configured or unreachable")
        # Check if tables exist
        inspector = inspect(current_engine)
        existing_tables = inspector.get_table_names()
        
        if not existing_tables:
            logger.info("Creating database tables...")
            Base.metadata.create_all(bind=current_engine)
            logger.info("Database tables created successfully")
        else:
            logger.info(f"Tables already exist: {existing_tables}")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise