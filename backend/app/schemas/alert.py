"""
Alert Schema
告警API数据验证模型
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class AlertBase(BaseModel):
    """告警基础模型"""
    service: str
    alert_type: str
    severity: str
    message: str
    status: Optional[str] = 'active'
    metric_value: Optional[Decimal] = None
    threshold: Optional[Decimal] = None


class AlertCreate(AlertBase):
    """创建告警请求模型"""
    pass


class AlertResponse(AlertBase):
    """告警响应模型"""
    id: int
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AlertListResponse(BaseModel):
    """告警列表响应模型"""
    total: int
    alerts: List[AlertResponse]


class AlertFilter(BaseModel):
    """告警过滤模型"""
    service: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    alert_type: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class AlertStats(BaseModel):
    """告警统计模型"""
    total: int
    active: int
    resolved: int
    by_severity: dict
