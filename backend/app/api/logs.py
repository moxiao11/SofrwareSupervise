"""
Log API
日志查询API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.services.log_service import LogService
from app.schemas.application_log import LogResponse, LogListResponse, LogFilter, LogCreate

router = APIRouter(prefix="/api/logs", tags=["日志服务"])


@router.get("/", response_model=LogListResponse, summary="获取日志列表")
async def get_logs(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    service: Optional[str] = Query(None, description="服务名称"),
    level: Optional[str] = Query(None, description="日志级别"),
    trace_id: Optional[str] = Query(None, description="Trace ID"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    db: Session = Depends(get_db)
):
    """
    获取日志列表，支持多种过滤条件
    """
    log_service = LogService(db)

    # 创建过滤条件
    filter = LogFilter(
        service=service,
        level=level,
        trace_id=trace_id,
        keyword=keyword,
        start_time=start_time,
        end_time=end_time
    )

    # 查询日志
    logs = log_service.get_logs(filter=filter, skip=skip, limit=limit)
    total = log_service.count_logs(filter=filter)

    return LogListResponse(total=total, logs=logs)


@router.get("/{log_id}", response_model=LogResponse, summary="获取日志详情")
async def get_log(log_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取日志详情
    """
    log_service = LogService(db)
    log = log_service.get_log_by_id(log_id)

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"日志 {log_id} 不存在"
        )

    return log


@router.post("/", response_model=LogResponse, status_code=status.HTTP_201_CREATED, summary="创建日志")
async def create_log(log_data: LogCreate, db: Session = Depends(get_db)):
    """
    创建日志记录
    """
    log_service = LogService(db)
    log = log_service.create_log(
        service=log_data.service,
        level=log_data.level,
        message=log_data.message,
        trace_id=log_data.trace_id,
        metadata=log_data.metadata
    )
    return log


@router.get("/stats/summary", summary="获取日志统计")
async def get_log_stats(db: Session = Depends(get_db)):
    """
    获取日志统计信息
    """
    log_service = LogService(db)

    # 统计各级别日志数量
    total = log_service.count_logs()
    error_count = log_service.count_logs(filter=LogFilter(level="ERROR"))
    warn_count = log_service.count_logs(filter=LogFilter(level="WARN"))
    info_count = log_service.count_logs(filter=LogFilter(level="INFO"))

    return {
        "total": total,
        "error": error_count,
        "warn": warn_count,
        "info": info_count
    }


@router.get("/services/list", summary="获取服务列表")
async def get_service_list(db: Session = Depends(get_db)):
    """
    获取所有有日志的服务列表
    """
    from sqlalchemy import distinct
    from app.models.application_log import ApplicationLog

    services = db.query(distinct(ApplicationLog.service)).all()
    return [s[0] for s in services]
