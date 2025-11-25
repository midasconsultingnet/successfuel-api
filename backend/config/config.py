import os
from pydantic import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    app_name: str = "SuccessFuel API"
    admin_email: str = "admin@successfuel.mg"
    secret_key: str = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    database_url: str = os.environ.get('DATABASE_URL', 'sqlite:///successfuel.db')
    jwt_secret_key: str = os.environ.get('JWT_SECRET_KEY', 'your-jwt-secret-key')
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    debug: bool = os.environ.get('DEBUG', 'True').lower() == 'true'

    class Config:
        env_file = ".env"

settings = Settings()