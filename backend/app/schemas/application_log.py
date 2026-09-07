"""
Application Log Schema
应用日志API数据验证模型
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class LogBase(BaseModel):
    """日志基础模型"""
    timestamp: datetime
    service: str
    level: str
    message: str
    trace_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class LogCreate(LogBase):
    """创建日志请求模型"""
    pass


class LogResponse(LogBase):
    """日志响应模型"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class LogListResponse(BaseModel):
    """日志列表响应模型"""
    total: int
    logs: list[LogResponse]


class LogFilter(BaseModel):
    """日志过滤模型"""
    service: Optional[str] = None
    level: Optional[str] = None
    trace_id: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    keyword: Optional[str] = None
