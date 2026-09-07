"""
Order Schemas
订单API数据验证模型
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class OrderBase(BaseModel):
    """订单基础模型"""
    user_id: int
    product_name: str
    amount: Decimal
    status: Optional[str] = 'pending'


class OrderCreate(OrderBase):
    """创建订单请求模型"""
    pass


class OrderResponse(OrderBase):
    """订单响应模型"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    """订单列表响应模型"""
    total: int
    orders: list[OrderResponse]
