from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey, Numeric, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from core.database import Base


class TradeType(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


class TradeStatus(str, enum.Enum):
    PENDING = "pending"
    OPEN = "open"
    CLOSED = "closed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class OrderType(str, enum.Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_MARKET = "STOP_MARKET"
    STOP_LIMIT = "STOP_LIMIT"
    TAKE_PROFIT_MARKET = "TAKE_PROFIT_MARKET"
    TRAILING_STOP_MARKET = "TRAILING_STOP_MARKET"


class MarketType(str, enum.Enum):
    SPOT = "spot"
    FUTURES = "futures"


class Trade(Base):
    __tablename__ = "trades"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    api_key_id = Column(UUID(as_uuid=True), ForeignKey("api_keys.id"), nullable=True)
    signal_id = Column(UUID(as_uuid=True), ForeignKey("signals.id"), nullable=True)
    binance_order_id = Column(String(100))
    client_order_id = Column(String(100))
    symbol = Column(String(20), nullable=False)
    trade_type = Column(Enum(TradeType), nullable=False)
    order_type = Column(Enum(OrderType), nullable=False, default=OrderType.MARKET)
    market_type = Column(Enum(MarketType), nullable=False, default=MarketType.SPOT)
    status = Column(Enum(TradeStatus), nullable=False, default=TradeStatus.PENDING)
    quantity = Column(Numeric(20, 8), nullable=False)
    entry_price = Column(Numeric(20, 8))
    exit_price = Column(Numeric(20, 8))
    stop_loss = Column(Numeric(20, 8))
    take_profit = Column(Numeric(20, 8))
    trailing_stop_percent = Column(Numeric(5, 2))
    leverage = Column(Integer, default=1)
    pnl = Column(Numeric(20, 8), default=0)
    pnl_percent = Column(Numeric(10, 4), default=0)
    fee = Column(Numeric(20, 8), default=0)
    is_auto_trade = Column(Boolean, default=False)
    is_testnet = Column(Boolean, default=False)
    notes = Column(Text)
    opened_at = Column(DateTime(timezone=True))
    closed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="trades")
    signal = relationship("Signal", back_populates="trades")


class Position(Base):
    __tablename__ = "positions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String(20), nullable=False)
    market_type = Column(Enum(MarketType), nullable=False)
    side = Column(Enum(TradeType), nullable=False)
    quantity = Column(Numeric(20, 8), nullable=False)
    entry_price = Column(Numeric(20, 8), nullable=False)
    current_price = Column(Numeric(20, 8))
    mark_price = Column(Numeric(20, 8))
    liquidation_price = Column(Numeric(20, 8))
    leverage = Column(Integer, default=1)
    margin = Column(Numeric(20, 8))
    unrealized_pnl = Column(Numeric(20, 8), default=0)
    realized_pnl = Column(Numeric(20, 8), default=0)
    stop_loss = Column(Numeric(20, 8))
    take_profit = Column(Numeric(20, 8))
    is_active = Column(Boolean, default=True)
    is_testnet = Column(Boolean, default=False)
    opened_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="positions")
