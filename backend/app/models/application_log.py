"""
Application Log Model
应用日志模型
"""
from sqlalchemy import Column, BigInteger, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class ApplicationLog(Base):
    """应用日志表模型"""
    __tablename__ = "application_logs"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    service = Column(String(100), nullable=False, index=True)
    level = Column(String(20), nullable=False, index=True)
    message = Column(Text, nullable=False)
    trace_id = Column(String(100), nullable=True, index=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<ApplicationLog(id={self.id}, service={self.service}, level={self.level})>"
