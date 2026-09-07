"""
Alert API
告警查询和管理API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.services.alert_service import AlertService
from app.schemas.alert import AlertResponse, AlertListResponse, AlertFilter, AlertStats

router = APIRouter(prefix="/api/alerts", tags=["告警服务"])


@router.get("/", response_model=AlertListResponse, summary="获取告警列表")
async def get_alerts(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    service: Optional[str] = Query(None, description="服务名称"),
    severity: Optional[str] = Query(None, description="严重程度"),
    status: Optional[str] = Query(None, description="状态"),
    alert_type: Optional[str] = Query(None, description="告警类型"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    db: Session = Depends(get_db)
):
    """
    获取告警列表，支持多种过滤条件
    """
    alert_service = AlertService(db)

    # 创建过滤条件
    filter = AlertFilter(
        service=service,
        severity=severity,
        status=status,
        alert_type=alert_type,
        start_time=start_time,
        end_time=end_time
    )

    # 查询告警
    alerts = alert_service.get_alerts(filter=filter, skip=skip, limit=limit)
    total = alert_service.count_alerts(filter=filter)

    return AlertListResponse(total=total, alerts=alerts)


@router.get("/{alert_id}", response_model=AlertResponse, summary="获取告警详情")
async def get_alert(alert_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取告警详情
    """
    alert_service = AlertService(db)
    alert = alert_service.get_alert_by_id(alert_id)

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"告警 {alert_id} 不存在"
        )

    return alert


@router.post("/{alert_id}/resolve", response_model=AlertResponse, summary="解决告警")
async def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    """
    解决指定告警
    """
    alert_service = AlertService(db)
    alert = alert_service.resolve_alert(alert_id)

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"告警 {alert_id} 不存在"
        )

    return alert


@router.post("/resolve/{service}", summary="解决服务的所有告警")
async def resolve_service_alerts(service: str, db: Session = Depends(get_db)):
    """
    解决指定服务的所有活跃告警
    """
    alert_service = AlertService(db)
    count = alert_service.resolve_alerts_by_service(service)

    return {
        "message": f"已解决 {service} 的 {count} 个告警",
        "count": count
    }


@router.get("/active/list", response_model=AlertListResponse, summary="获取活跃告警")
async def get_active_alerts(
    service: Optional[str] = Query(None, description="服务名称"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    获取所有活跃告警
    """
    alert_service = AlertService(db)
    filter = AlertFilter(status='active')
    if service:
        filter.service = service

    alerts = alert_service.get_alerts(filter=filter, skip=skip, limit=limit)
    total = alert_service.count_alerts(filter=filter)

    return AlertListResponse(total=total, alerts=alerts)


@router.get("/stats/summary", response_model=AlertStats, summary="获取告警统计")
async def get_alert_stats(db: Session = Depends(get_db)):
    """
    获取告警统计信息
    """
    alert_service = AlertService(db)
    stats = alert_service.get_alert_stats()

    return stats


@router.get("/rules/list", summary="获取告警规则列表")
async def get_alert_rules(db: Session = Depends(get_db)):
    """
    获取所有告警规则
    """
    alert_service = AlertService(db)
    rules = alert_service.rule_engine.get_rules()

    return {
        "total": len(rules),
        "rules": rules
    }


@router.post("/check", summary="手动检查指标并生成告警")
async def check_metrics(
    service: str = Query(..., description="服务名称"),
    cpu_usage: Optional[float] = Query(None, description="CPU使用率"),
    memory_usage: Optional[float] = Query(None, description="内存使用率"),
    api_latency: Optional[float] = Query(None, description="API延迟"),
    db_query_time: Optional[float] = Query(None, description="数据库查询时间"),
    error_rate: Optional[float] = Query(None, description="错误率"),
    disk_usage: Optional[float] = Query(None, description="磁盘使用率"),
    db: Session = Depends(get_db)
):
    """
    手动检查指标并生成告警
    """
    alert_service = AlertService(db)

    # 构建指标字典
    metrics = {}
    if cpu_usage is not None:
        metrics["cpu_usage"] = cpu_usage
    if memory_usage is not None:
        metrics["memory_usage"] = memory_usage
    if api_latency is not None:
        metrics["api_latency"] = api_latency
    if db_query_time is not None:
        metrics["db_query_time"] = db_query_time
    if error_rate is not None:
        metrics["error_rate"] = error_rate
    if disk_usage is not None:
        metrics["disk_usage"] = disk_usage

    # 检查并创建告警
    alerts = alert_service.check_and_create_alerts(service, metrics)

    return {
        "message": f"检查完成，触发 {len(alerts)} 个告警",
        "alerts_count": len(alerts),
        "alerts": [
            {
                "id": alert.id,
                "severity": alert.severity,
                "type": alert.alert_type,
                "message": alert.message
            }
            for alert in alerts
        ]
    }
