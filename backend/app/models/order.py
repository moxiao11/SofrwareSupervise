"""
Order Model
订单模型
"""
from sqlalchemy import Column, BigInteger, String, DateTime, Numeric
from sqlalchemy.sql import func
from app.core.database import Base


class Order(Base):
    """订单表模型"""
    __tablename__ = "orders"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    product_name = Column(String(200), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(50), default='pending')
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<Order(id={self.id}, user_id={self.user_id}, product={self.product_name}, amount={self.amount})>"
