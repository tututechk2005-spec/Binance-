from pydantic import BaseModel
from typing import Optional, List, Any, Dict
from datetime import datetime
import uuid


class SignalResponse(BaseModel):
    id: uuid.UUID
    symbol: str
    signal_type: str
    status: str
    confidence_score: float
    entry_price: float
    stop_loss: float
    take_profit_1: Optional[float] = None
    take_profit_2: Optional[float] = None
    take_profit_3: Optional[float] = None
    timeframe: str
    risk_reward_ratio: Optional[float] = None
    indicators: Optional[Dict[str, Any]] = None
    market_structure: Optional[str] = None
    trend: Optional[str] = None
    bos_detected: bool = False
    choch_detected: bool = False
    notes: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SignalListResponse(BaseModel):
    signals: List[SignalResponse]
    total: int
    page: int
    per_page: int
    pages: int
