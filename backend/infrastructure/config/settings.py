"""
Infrastructure Configuration Settings
Author: Hugo Francisco Luis Inclan
Copyright (c) 2026 Hugo Francisco Luis Inclan
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    app_name: str = "Radio-Mundial API"
    environment: str = "production"
    host: str = "0.0.0.0"
    port: int = 8000
    allowed_origins: list[str] = Field(
        default=[
            "http://localhost:5296",
            "http://127.0.0.1:5296",
            "http://localhost:5000",
            "http://localhost:8080",
            "https://radio-mundial.pages.dev",
            "*"
        ]
    )
    seed_path: str = "data/seed_stations.json"
    enable_warmup: bool = True

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
