"""
Infrastructure Configuration Settings
Author: Hugo Francisco Luis Inclan
Copyright (c) 2026 Hugo Francisco Luis Inclan
"""

import json
from typing import Union
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    app_name: str = "Radio-Mundial API"
    environment: str = "production"
    host: str = "0.0.0.0"
    port: int = 8000
    allowed_origins: Union[str, list[str]] = Field(
        default=[
            "http://localhost:5296",
            "http://127.0.0.1:5296",
            "http://localhost:5000",
            "http://localhost:8080",
            "https://radio-mundial.hugofranciscoluis.workers.dev",
            "https://radio-mundial.pages.dev",
            "*"
        ]
    )
    seed_path: str = "data/seed_stations.json"
    enable_warmup: bool = True
    notification_email: str = "hugofranciscoluisinclan@gmail.com"

    @field_validator("allowed_origins", mode="after")
    @classmethod
    def normalize_origins(cls, v) -> list[str]:
        if isinstance(v, list):
            return [str(x).strip() for x in v if str(x).strip()]
        if isinstance(v, str):
            val = v.strip()
            if not val:
                return ["*"]
            # Handle JSON array format e.g. ["*"] or ['*']
            if val.startswith("[") and val.endswith("]"):
                try:
                    parsed = json.loads(val)
                    if isinstance(parsed, list):
                        return [str(x).strip() for x in parsed if str(x).strip()]
                except Exception:
                    pass
                # Fallback for single quotes inside brackets: ['*']
                raw_items = val.strip("[]").split(",")
                cleaned = [i.strip(" \"'") for i in raw_items if i.strip(" \"'")]
                return cleaned if cleaned else ["*"]
            # Handle comma-separated list
            if "," in val:
                return [i.strip() for i in val.split(",") if i.strip()]
            # Single origin or wildcard
            return [val]
        return ["*"]

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
