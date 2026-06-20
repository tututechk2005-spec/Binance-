from pydantic import BaseModel
from typing import Optional


class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None


class UpdateTradingSettingsRequest(BaseModel):
    auto_trading_enabled: Optional[bool] = None
    risk_percent: Optional[float] = None
    max_trades_per_day: Optional[int] = None


class ApiKeyCreateRequest(BaseModel):
    label: str
    api_key: str
    secret_key: str
    network_type: str = "spot_testnet"
    permissions: Optional[str] = "READ,TRADE"


class ApiKeyResponse(BaseModel):
    id: str
    label: str
    network_type: str
    is_active: bool
    is_verified: bool
    permissions: Optional[str]
    created_at: object

    class Config:
        from_attributes = True
