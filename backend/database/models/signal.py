from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey, Numeric, Text, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from core.database import Base


class SignalType(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


class SignalStatus(str, enum.Enum):
    ACTIVE = "active"
    TRIGGERED = "triggered"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class Signal(Base):
    __tablename__ = "signals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(20), nullable=False, index=True)
    signal_type = Column(Enum(SignalType), nullable=False)
    status = Column(Enum(SignalStatus), default=SignalStatus.ACTIVE)
    confidence_score = Column(Numeric(5, 2), nullable=False)
    entry_price = Column(Numeric(20, 8), nullable=False)
    stop_loss = Column(Numeric(20, 8), nullable=False)
    take_profit_1 = Column(Numeric(20, 8))
    take_profit_2 = Column(Numeric(20, 8))
    take_profit_3 = Column(Numeric(20, 8))
    timeframe = Column(String(10), nullable=False, default="1h")
    risk_reward_ratio = Column(Numeric(5, 2))
    indicators = Column(JSON)
    analysis_data = Column(JSON)
    market_structure = Column(String(50))
    trend = Column(String(20))
    liquidity_zones = Column(JSON)
    order_blocks = Column(JSON)
    fair_value_gaps = Column(JSON)
    smart_money_concepts = Column(JSON)
    rsi_value = Column(Numeric(5, 2))
    macd_signal = Column(String(20))
    ema_alignment = Column(String(20))
    atr_value = Column(Numeric(20, 8))
    volume_analysis = Column(String(50))
    bos_detected = Column(Boolean, default=False)
    choch_detected = Column(Boolean, default=False)
    notes = Column(Text)
    expires_at = Column(DateTime(timezone=True))
    triggered_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    trades = relationship("Trade", back_populates="signal")
