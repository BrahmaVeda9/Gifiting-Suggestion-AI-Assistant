import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Dearly API Phase 1"
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "dummy_key")
    supabase_url: str = os.getenv("SUPABASE_URL", "dummy_url")
    supabase_key: str = os.getenv("SUPABASE_KEY", "dummy_key")

    class Config:
        env_file = ".env"

settings = Settings()
