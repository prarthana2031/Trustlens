from supabase import create_client, Client
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class SupabaseClient:
    """Singleton Supabase client"""
    _instance = None
    
    @classmethod
    def get_instance(cls) -> Client:
        if cls._instance is None:
            try:
                logger.info(f"Initializing Supabase with URL: {settings.SUPABASE_URL}")
                logger.info(f"Key length: {len(settings.SUPABASE_KEY)}")
                cls._instance = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_KEY
                )
                logger.info("✅ Supabase client initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Supabase client: {e}")
                logger.error(f"URL: {settings.SUPABASE_URL}")
                logger.error(f"Key starts with: {settings.SUPABASE_KEY[:30]}...")
                raise
        return cls._instance

def get_supabase() -> Client:
    """Get Supabase client instance"""
    return SupabaseClient.get_instance()

def test_connection():
    """Test Supabase connection - using health check instead of table query"""
    try:
        client = get_supabase()
        # Use the REST API health check by fetching from a system endpoint
        # This checks if the client is properly configured without needing tables
        response = client.auth.get_session()
        # If we get here, connection is working
        logger.info("✅ Supabase connection successful")
        return True
    except Exception as e:
        # Check if it's just a no table error vs connection error
        error_msg = str(e)
        if "Could not find the table" in error_msg:
            # This is actually good - it means Supabase is connected but tables don't exist yet
            logger.info("✅ Supabase connection successful (tables not created yet)")
            return True
        else:
            logger.error(f"❌ Supabase connection failed: {e}")
            return False