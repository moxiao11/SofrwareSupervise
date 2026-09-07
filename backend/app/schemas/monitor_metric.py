"""
Monitor Metric Schema
监控指标API数据验证模型
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class MetricBase(BaseModel):
    """指标基础模型"""
    service: str
    metric_name: str
    metric_value: Decimal
    unit: Optional[str] = None
    timestamp: datetime


class MetricCreate(MetricBase):
    """创建指标请求模型"""
    pass


class MetricResponse(MetricBase):
    """指标响应模型"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class MetricListResponse(BaseModel):
    """指标列表响应模型"""
    total: int
    metrics: List[MetricResponse]


class MetricStats(BaseModel):
    """指标统计模型"""
    metric_name: str
    service: str
    avg_value: Decimal
    min_value: Decimal
    max_value: Decimal
    count: int


class MetricFilter(BaseModel):
    """指标过滤模型"""
    service: Optional[str] = None
    metric_name: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
