import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = os.getenv("APP_NAME", "Resume Scoring API")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    API_V1_PREFIX: str = os.getenv("API_V1_PREFIX", "/api/v1")
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # CORS
    ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    
    def validate(self):
        """Validate required settings"""
        required = ["SUPABASE_URL", "SUPABASE_KEY", "DATABASE_URL"]
        missing = [r for r in required if not getattr(self, r)]
        if missing:
            raise ValueError(f"Missing required environment variables: {missing}")

# Create global settings instance
settings = Settings()
settings.validate()