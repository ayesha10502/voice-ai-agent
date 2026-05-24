from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    frontend_url: str = "http://localhost:3000"

    # Vapi
    vapi_api_key: str = ""
    vapi_phone_number_id: str = ""
    vapi_base_url: str = "https://api.vapi.ai"

    # Webhook
    webhook_base_url: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
