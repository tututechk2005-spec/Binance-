from sqlalchemy import Column, String, Boolean, DateTime, Enum, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from core.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"


class SubscriptionPlan(str, enum.Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    phone = Column(String(20))
    avatar_url = Column(String(500))
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    subscription_plan = Column(Enum(SubscriptionPlan), default=SubscriptionPlan.FREE)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(255))
    auto_trading_enabled = Column(Boolean, default=False)
    risk_percent = Column(Integer, default=1)
    max_trades_per_day = Column(Integer, default=10)
    country = Column(String(100))
    timezone = Column(String(50), default="UTC")
    referral_code = Column(String(20), unique=True)
    referred_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    last_login = Column(DateTime(timezone=True))
    login_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    api_keys = relationship("ApiKey", back_populates="user", cascade="all, delete-orphan")
    trades = relationship("Trade", back_populates="user", cascade="all, delete-orphan")
    positions = relationship("Position", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    subscription = relationship("Subscription", back_populates="user", uselist=False)
    wallet = relationship("Wallet", back_populates="user", uselist=False)
    transactions = relationship("Transaction", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
