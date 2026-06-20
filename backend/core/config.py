from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator
from typing import List, Optional
import secrets


class Settings(BaseSettings):
    APP_NAME: str = "Binance AI Trader Pro"
    APP_ENV: str = "production"
    APP_SECRET_KEY: str = secrets.token_urlsafe(64)
    DEBUG: bool = False
    ALLOWED_ORIGINS: List[str] = ["http://localhost", "http://localhost:3000", "http://localhost:80"]

    POSTGRES_USER: str = "batpro"
    POSTGRES_PASSWORD: str = "batpro_secret"
    POSTGRES_DB: str = "batpro_db"
    DATABASE_URL: str = "postgresql+asyncpg://batpro:batpro_secret@postgres:5432/batpro_db"
    DATABASE_SYNC_URL: str = "postgresql://batpro:batpro_secret@postgres:5432/batpro_db"

    REDIS_PASSWORD: str = "redis_secret"
    REDIS_URL: str = "redis://:redis_secret@redis:6379/0"

    JWT_SECRET_KEY: str = secrets.token_urlsafe(64)
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    ENCRYPTION_KEY: str = secrets.token_urlsafe(32)[:32]

    BINANCE_SPOT_MAINNET_BASE_URL: str = "https://api.binance.com"
    BINANCE_FUTURES_MAINNET_BASE_URL: str = "https://fapi.binance.com"
    BINANCE_SPOT_TESTNET_BASE_URL: str = "https://testnet.binance.vision"
    BINANCE_FUTURES_TESTNET_BASE_URL: str = "https://testnet.binancefuture.com"
    BINANCE_WS_MAINNET: str = "wss://stream.binance.com:9443"
    BINANCE_WS_TESTNET: str = "wss://testnet.binance.vision"

    AI_SIGNAL_INTERVAL_SECONDS: int = 60
    AI_CONFIDENCE_THRESHOLD: float = 70.0
    DEFAULT_RISK_PERCENT: float = 1.0
    MAX_RISK_PERCENT: float = 5.0

    STRIPE_PUBLIC_KEY: str = ""
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    PAYPAL_CLIENT_ID: str = ""
    PAYPAL_CLIENT_SECRET: str = ""
    PAYPAL_MODE: str = "sandbox"

    MTN_SUBSCRIPTION_KEY: str = ""
    MTN_API_USER: str = ""
    MTN_API_KEY: str = ""
    MTN_BASE_URL: str = "https://sandbox.momodeveloper.mtn.com"
    MTN_CALLBACK_URL: str = ""
    MTN_ENVIRONMENT: str = "sandbox"

    AIRTEL_CLIENT_ID: str = ""
    AIRTEL_CLIENT_SECRET: str = ""
    AIRTEL_BASE_URL: str = "https://openapi.airtel.africa"
    AIRTEL_CALLBACK_URL: str = ""

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@batpro.app"

    ADMIN_EMAIL: str = "admin@batpro.app"
    ADMIN_PASSWORD: str = "Admin@123456"
    ADMIN_USERNAME: str = "admin"

    CELERY_BROKER_URL: str = "redis://:redis_secret@redis:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://:redis_secret@redis:6379/2"

    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "/app/logs/app.log"

    @validator("ALLOWED_ORIGINS", pre=True)
    def parse_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
