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
                cls._instance = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_KEY
                )
                logger.info("✅ Supabase client initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Supabase client: {e}")
                raise
        return cls._instance

def get_supabase() -> Client:
    """Get Supabase client instance"""
    return SupabaseClient.get_instance()

def test_connection():
    """Test Supabase connection"""
    try:
        client = get_supabase()
        # Try to list buckets (simple operation)
        client.storage.list_buckets()
        logger.info("✅ Supabase connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Supabase connection failed: {e}")
        return False