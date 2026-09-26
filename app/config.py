from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Auto Ticket Classification using Flow Designer"
    database_url: str = "sqlite:///./data/tickets.db"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta/models"
    smtp_enabled: bool = False
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from: str = "helpdesk@example.edu"
    cors_origins: str = "*"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()
