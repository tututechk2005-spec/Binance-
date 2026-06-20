from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey, Numeric, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from core.database import Base


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class PaymentProvider(str, enum.Enum):
    STRIPE = "stripe"
    PAYPAL = "paypal"
    MTN = "mtn"
    AIRTEL = "airtel"
    CRYPTO = "crypto"


class TransactionType(str, enum.Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    SUBSCRIPTION = "subscription"
    REFUND = "refund"


class PlanInterval(str, enum.Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class Plan(Base):
    __tablename__ = "plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False)
    slug = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    price_monthly = Column(Numeric(10, 2), nullable=False)
    price_quarterly = Column(Numeric(10, 2))
    price_yearly = Column(Numeric(10, 2))
    max_api_keys = Column(Integer, default=1)
    max_auto_trades_per_day = Column(Integer, default=5)
    max_signals_per_day = Column(Integer, default=10)
    features = Column(Text)
    is_active = Column(Boolean, default=True)
    stripe_price_id_monthly = Column(String(100))
    stripe_price_id_yearly = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    subscriptions = relationship("Subscription", back_populates="plan")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id"), nullable=False)
    status = Column(String(20), default="active")
    interval = Column(Enum(PlanInterval), default=PlanInterval.MONTHLY)
    stripe_subscription_id = Column(String(100))
    stripe_customer_id = Column(String(100))
    paypal_subscription_id = Column(String(100))
    current_period_start = Column(DateTime(timezone=True))
    current_period_end = Column(DateTime(timezone=True))
    cancel_at_period_end = Column(Boolean, default=False)
    cancelled_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="subscription")
    plan = relationship("Plan", back_populates="subscriptions")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=True)
    provider = Column(Enum(PaymentProvider), nullable=False)
    external_id = Column(String(200))
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(10), default="USD")
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    provider_response = Column(Text)
    phone_number = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User")


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    balance = Column(Numeric(20, 8), default=0)
    currency = Column(String(10), default="USD")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="wallet")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Numeric(20, 8), nullable=False)
    currency = Column(String(10), default="USD")
    reference = Column(String(200))
    description = Column(Text)
    balance_before = Column(Numeric(20, 8))
    balance_after = Column(Numeric(20, 8))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="transactions")
