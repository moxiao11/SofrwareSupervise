"""
Metrics API
监控指标查询API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db
from app.services.monitoring_service import MonitoringService
from app.schemas.monitor_metric import MetricResponse, MetricListResponse, MetricFilter

router = APIRouter(prefix="/api/metrics", tags=["监控指标"])


@router.get("/", response_model=MetricListResponse, summary="获取指标列表")
async def get_metrics(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    service: Optional[str] = Query(None, description="服务名称"),
    metric_name: Optional[str] = Query(None, description="指标名称"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    db: Session = Depends(get_db)
):
    """
    获取监控指标列表，支持多种过滤条件
    """
    monitoring_service = MonitoringService(db)

    # 创建过滤条件
    filter = MetricFilter(
        service=service,
        metric_name=metric_name,
        start_time=start_time,
        end_time=end_time
    )

    # 查询指标
    metrics = monitoring_service.get_metrics(filter=filter, skip=skip, limit=limit)
    total = monitoring_service.count_metrics(filter=filter)

    return MetricListResponse(total=total, metrics=metrics)


@router.get("/latest/{service}/{metric_name}", response_model=MetricResponse, summary="获取最新指标")
async def get_latest_metric(
    service: str,
    metric_name: str,
    db: Session = Depends(get_db)
):
    """
    获取指定服务和指标的最新值
    """
    monitoring_service = MonitoringService(db)
    metric = monitoring_service.get_latest_metric(service, metric_name)

    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到 {service} 的 {metric_name} 指标"
        )

    return metric


@router.get("/stats/{service}/{metric_name}", summary="获取指标统计")
async def get_metric_stats(
    service: str,
    metric_name: str,
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    db: Session = Depends(get_db)
):
    """
    获取指标统计信息（平均值、最小值、最大值）
    """
    monitoring_service = MonitoringService(db)
    stats = monitoring_service.get_metric_stats(
        service=service,
        metric_name=metric_name,
        start_time=start_time,
        end_time=end_time
    )

    return {
        "service": service,
        "metric_name": metric_name,
        "stats": stats
    }


@router.get("/services/list", summary="获取服务列表")
async def get_service_list(db: Session = Depends(get_db)):
    """
    获取所有有监控指标的服务列表
    """
    from sqlalchemy import distinct
    from app.models.monitor_metric import MonitorMetric

    services = db.query(distinct(MonitorMetric.service)).all()
    return [s[0] for s in services]


@router.get("/metrics/list", summary="获取指标名称列表")
async def get_metric_list(
    service: Optional[str] = Query(None, description="服务名称"),
    db: Session = Depends(get_db)
):
    """
    获取所有指标名称列表
    """
    from sqlalchemy import distinct
    from app.models.monitor_metric import MonitorMetric

    query = db.query(distinct(MonitorMetric.metric_name))
    if service:
        query = query.filter(MonitorMetric.service == service)

    metrics = query.all()
    return [m[0] for m in metrics]


@router.get("/dashboard/summary", summary="获取仪表盘摘要")
async def get_dashboard_summary(db: Session = Depends(get_db)):
    """
    获取仪表盘摘要信息
    """
    monitoring_service = MonitoringService(db)

    # 获取系统指标
    cpu_metric = monitoring_service.get_latest_metric("system", "cpu_usage")
    memory_metric = monitoring_service.get_latest_metric("system", "memory_usage")

    # 获取应用指标
    latency_metric = monitoring_service.get_latest_metric("order-service", "api_latency")

    return {
        "cpu_usage": float(cpu_metric.metric_value) if cpu_metric else None,
        "memory_usage": float(memory_metric.metric_value) if memory_metric else None,
        "api_latency": float(latency_metric.metric_value) if latency_metric else None,
        "timestamp": cpu_metric.timestamp.isoformat() if cpu_metric else None
    }
