"""
Production configuration for MessageCraft
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application Mode
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    IS_PRODUCTION: bool = os.getenv("ENVIRONMENT", "development").lower() == "production"
    
    # API Configuration
    API_VERSION: str = "v1"
    API_PREFIX: str = f"/api/{API_VERSION}"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # Database
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # AI Configuration
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/v1/auth/google/callback")
    
    # Stripe Configuration
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    STRIPE_PRICE_BASIC: str = os.getenv("STRIPE_PRICE_BASIC", "")
    STRIPE_PRICE_PROFESSIONAL: str = os.getenv("STRIPE_PRICE_PROFESSIONAL", "")
    STRIPE_PRICE_AGENCY: str = os.getenv("STRIPE_PRICE_AGENCY", "")
    STRIPE_PRICE_CREDITS_10: str = os.getenv("STRIPE_PRICE_CREDITS_10", "")  # 10 credits
    STRIPE_PRICE_CREDITS_50: str = os.getenv("STRIPE_PRICE_CREDITS_50", "")  # 50 credits
    STRIPE_PRICE_CREDITS_100: str = os.getenv("STRIPE_PRICE_CREDITS_100", "")  # 100 credits
    
    # Frontend URLs
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    SUCCESS_URL: str = os.getenv("SUCCESS_URL", f"{FRONTEND_URL}/success")
    CANCEL_URL: str = os.getenv("CANCEL_URL", f"{FRONTEND_URL}/cancel")
    
    # Production Mode Settings
    FREE_TIER_KIT_LIMIT: int = 1  # Users can generate only 1 kit for free
    CREDITS_PER_KIT: int = 1  # 1 credit = 1 kit generation
    
    # Credit Packages
    CREDIT_PACKAGES = {
        "credits_10": {"credits": 10, "price": 99},  # $99 for 10 credits
        "credits_50": {"credits": 50, "price": 399},  # $399 for 50 credits  
        "credits_100": {"credits": 100, "price": 699}  # $699 for 100 credits
    }
    
    # CORS Origins
    @property
    def CORS_ORIGINS(self) -> list:
        if self.IS_PRODUCTION:
            return [self.FRONTEND_URL]
        return ["*"]  # Allow all in development
    
    class Config:
        case_sensitive = True
        env_file = ".env"

# Create settings instance
settings = Settings()