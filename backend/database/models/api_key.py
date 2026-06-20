from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from core.database import Base


class NetworkType(str, enum.Enum):
    SPOT_MAINNET = "spot_mainnet"
    FUTURES_MAINNET = "futures_mainnet"
    SPOT_TESTNET = "spot_testnet"
    FUTURES_TESTNET = "futures_testnet"


class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    label = Column(String(100), nullable=False)
    encrypted_api_key = Column(Text, nullable=False)
    encrypted_secret_key = Column(Text, nullable=False)
    network_type = Column(Enum(NetworkType), nullable=False, default=NetworkType.SPOT_TESTNET)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    permissions = Column(String(255), default="READ")
    last_used = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="api_keys")
