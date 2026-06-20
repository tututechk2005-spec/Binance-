from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from core.database import Base


class NotificationType(str, enum.Enum):
    SIGNAL = "signal"
    TRADE = "trade"
    PAYMENT = "payment"
    SYSTEM = "system"
    ALERT = "alert"
    NEWS = "news"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    notification_type = Column(Enum(NotificationType), default=NotificationType.SYSTEM)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    data = Column(JSON)
    is_read = Column(Boolean, default=False)
    is_email_sent = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="notifications")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False)
    resource = Column(String(100))
    resource_id = Column(String(100))
    old_value = Column(Text)
    new_value = Column(Text)
    ip_address = Column(String(50))
    user_agent = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="audit_logs")


class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    level = Column(String(20), nullable=False)
    service = Column(String(100))
    message = Column(Text, nullable=False)
    data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
