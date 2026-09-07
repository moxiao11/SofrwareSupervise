"""
Monitor Metric Model
监控指标模型
"""
from sqlalchemy import Column, BigInteger, String, DateTime, Numeric
from sqlalchemy.sql import func
from app.core.database import Base


class MonitorMetric(Base):
    """监控指标表模型"""
    __tablename__ = "monitor_metrics"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    service = Column(String(100), nullable=False, index=True)
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(Numeric(20, 4), nullable=False)
    unit = Column(String(50), nullable=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<MonitorMetric(service={self.service}, metric={self.metric_name}, value={self.metric_value})>"
