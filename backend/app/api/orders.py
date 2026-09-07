"""
Order Service
订单服务API - 支持故障注入
"""
import time
import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

from app.core.database import get_db
from app.core.logging import get_logger
from app.models.order import Order
from app.schemas.order import OrderResponse, OrderCreate, OrderListResponse
from app.services.log_service import LogService
from app.services.monitoring_service import MonitoringService

router = APIRouter(prefix="/api/orders", tags=["订单服务"])

# 故障模式开关
FAULT_MODE = os.getenv("FAULT_MODE", "false").lower() == "true"
SLOW_SQL_ENABLED = False
LATENCY_ENABLED = False
ERROR_ENABLED = False

# 慢SQL阈值（毫秒）
SLOW_SQL_THRESHOLD_MS = 1000


@router.get("/", response_model=OrderListResponse, summary="获取订单列表")
async def get_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    获取订单列表
    """
    # 故障注入：接口延迟
    if LATENCY_ENABLED:
        time.sleep(3)  # 模拟3秒延迟

    # 故障注入：HTTP 500错误
    if ERROR_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="模拟订单服务内部错误"
        )

    orders = db.query(Order).offset(skip).limit(limit).all()
    total = db.query(Order).count()

    return OrderListResponse(total=total, orders=orders)


@router.get("/{order_id}", response_model=OrderResponse, summary="获取订单详情")
async def get_order(order_id: int, db: Session = Depends(get_db)):
    """
    根据订单ID获取订单详情
    """
    # 故障注入：接口延迟
    if LATENCY_ENABLED:
        time.sleep(3)

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"订单 {order_id} 不存在"
        )
    return order


@router.get("/user/{user_id}", response_model=OrderListResponse, summary="获取用户订单")
async def get_user_orders(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    获取指定用户的订单列表
    这是制造慢SQL的关键接口
    """
    # 故障注入：接口延迟
    if LATENCY_ENABLED:
        time.sleep(3)

    # 创建日志服务
    log_service = LogService(db)
    monitoring_service = MonitoringService(db)
    logger = get_logger(service="order-service")

    # 故障注入：慢SQL（不创建索引，大量数据查询）
    if SLOW_SQL_ENABLED:
        # 执行全表扫描查询
        start_time = time.time()
        orders = db.query(Order).filter(Order.user_id == user_id).offset(skip).limit(limit).all()
        total = db.query(Order).filter(Order.user_id == user_id).count()
        query_time_ms = (time.time() - start_time) * 1000

        # 记录慢SQL日志
        sql = f"SELECT * FROM orders WHERE user_id = {user_id}"
        logger.warning(f"Slow SQL detected: {query_time_ms:.2f}ms - {sql}")

        # 保存到数据库日志
        log_service.log_slow_sql(
            service="order-service",
            sql=sql,
            duration_ms=query_time_ms,
            trace_id=None
        )

        # 采集数据库指标
        monitoring_service.collect_database_metrics(
            service="order-service",
            query_time_ms=query_time_ms
        )

        return OrderListResponse(total=total, orders=orders)

    # 正常查询
    start_time = time.time()
    orders = db.query(Order).filter(Order.user_id == user_id).offset(skip).limit(limit).all()
    total = db.query(Order).filter(Order.user_id == user_id).count()
    query_time_ms = (time.time() - start_time) * 1000

    # 采集数据库指标
    monitoring_service.collect_database_metrics(
        service="order-service",
        query_time_ms=query_time_ms
    )

    # 如果查询时间超过阈值，也记录为慢SQL
    if query_time_ms > SLOW_SQL_THRESHOLD_MS:
        sql = f"SELECT * FROM orders WHERE user_id = {user_id}"
        logger.warning(f"Slow SQL detected: {query_time_ms:.2f}ms - {sql}")
        log_service.log_slow_sql(
            service="order-service",
            sql=sql,
            duration_ms=query_time_ms,
            trace_id=None
        )
    else:
        logger.info(f"Query user {user_id} orders: {query_time_ms:.2f}ms")

    return OrderListResponse(total=total, orders=orders)


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED, summary="创建订单")
async def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    """
    创建新订单
    """
    # 故障注入：接口延迟
    if LATENCY_ENABLED:
        time.sleep(3)

    order = Order(
        user_id=order_data.user_id,
        product_name=order_data.product_name,
        amount=order_data.amount,
        status=order_data.status
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


# ============================================
# 故障注入控制接口
# ============================================

@router.post("/debug/enable-slow-sql", summary="启用慢SQL故障")
async def enable_slow_sql(enabled: bool = True):
    """
    启用/禁用慢SQL故障
    """
    global SLOW_SQL_ENABLED
    SLOW_SQL_ENABLED = enabled
    return {
        "message": f"慢SQL故障已{'启用' if enabled else '禁用'}",
        "status": SLOW_SQL_ENABLED
    }


@router.post("/debug/enable-latency", summary="启用接口延迟故障")
async def enable_latency(enabled: bool = True):
    """
    启用/禁用接口延迟故障
    """
    global LATENCY_ENABLED
    LATENCY_ENABLED = enabled
    return {
        "message": f"接口延迟故障已{'启用' if enabled else '禁用'}",
        "status": LATENCY_ENABLED
    }


@router.post("/debug/enable-error", summary="启用HTTP 500错误故障")
async def enable_error(enabled: bool = True):
    """
    启用/禁用HTTP 500错误故障
    """
    global ERROR_ENABLED
    ERROR_ENABLED = enabled
    return {
        "message": f"HTTP 500错误故障已{'启用' if enabled else '禁用'}",
        "status": ERROR_ENABLED
    }


@router.get("/debug/status", summary="获取故障注入状态")
async def get_fault_status():
    """
    获取当前所有故障注入的状态
    """
    return {
        "slow_sql_enabled": SLOW_SQL_ENABLED,
        "latency_enabled": LATENCY_ENABLED,
        "error_enabled": ERROR_ENABLED
    }


@router.post("/debug/reset", summary="重置所有故障")
async def reset_all_faults():
    """
    重置所有故障注入
    """
    global SLOW_SQL_ENABLED, LATENCY_ENABLED, ERROR_ENABLED
    SLOW_SQL_ENABLED = False
    LATENCY_ENABLED = False
    ERROR_ENABLED = False
    return {
        "message": "所有故障已重置",
        "status": "normal"
    }
