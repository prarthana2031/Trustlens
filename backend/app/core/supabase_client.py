from supabase import create_client, Client
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class SupabaseClient:
    _instance = None
    _client: Client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize Supabase client"""
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            logger.warning("Supabase credentials not configured")
            self._client = None
        else:
            try:
                self._client = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_KEY
                )
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {str(e)}")
                self._client = None
    
    def get_client(self) -> Client:
        """Get Supabase client instance"""
        if self._client is None:
            raise Exception("Supabase client not initialized")
        return self._client
    
    def is_available(self) -> bool:
        """Check if Supabase is available"""
        return self._client is not None

# Global instance
supabase_client = SupabaseClient()