"""
Alert Model
告警模型
"""
from sqlalchemy import Column, BigInteger, String, DateTime, Numeric, Text
from sqlalchemy.sql import func
from app.core.database import Base


class Alert(Base):
    """告警表模型"""
    __tablename__ = "alerts"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    service = Column(String(100), nullable=False, index=True)
    alert_type = Column(String(100), nullable=False, index=True)
    severity = Column(String(20), nullable=False, index=True)  # P0, P1, P2, P3
    message = Column(Text, nullable=False)
    status = Column(String(20), default='active', index=True)  # active, resolved
    metric_value = Column(Numeric(20, 4), nullable=True)
    threshold = Column(Numeric(20, 4), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    resolved_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Alert(id={self.id}, service={self.service}, severity={self.severity}, type={self.alert_type})>"
