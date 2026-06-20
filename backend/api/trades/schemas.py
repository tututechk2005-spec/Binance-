from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid


class TradeResponse(BaseModel):
    id: uuid.UUID
    symbol: str
    trade_type: str
    order_type: str
    market_type: str
    status: str
    quantity: float
    entry_price: Optional[float] = None
    exit_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    leverage: int = 1
    pnl: float = 0
    pnl_percent: float = 0
    fee: float = 0
    is_auto_trade: bool = False
    is_testnet: bool = False
    opened_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TradeListResponse(BaseModel):
    trades: List[TradeResponse]
    total: int
    page: int
    per_page: int
    pages: int


class CreateTradeRequest(BaseModel):
    symbol: str
    trade_type: str
    order_type: str = "MARKET"
    market_type: str = "spot"
    quantity: float
    price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    leverage: int = 1
    api_key_id: Optional[str] = None


class PositionResponse(BaseModel):
    id: uuid.UUID
    symbol: str
    market_type: str
    side: str
    quantity: float
    entry_price: float
    current_price: Optional[float] = None
    leverage: int = 1
    unrealized_pnl: float = 0
    realized_pnl: float = 0
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    is_active: bool = True
    is_testnet: bool = False
    opened_at: Optional[datetime] = None

    class Config:
        from_attributes = True
