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
from app.models.order import Order
from app.schemas.order import OrderResponse, OrderCreate, OrderListResponse

router = APIRouter(prefix="/api/orders", tags=["订单服务"])

# 故障模式开关
FAULT_MODE = os.getenv("FAULT_MODE", "false").lower() == "true"
SLOW_SQL_ENABLED = False
LATENCY_ENABLED = False
ERROR_ENABLED = False


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

    # 故障注入：慢SQL（不创建索引，大量数据查询）
    if SLOW_SQL_ENABLED:
        # 执行全表扫描查询
        start_time = time.time()
        orders = db.query(Order).filter(Order.user_id == user_id).offset(skip).limit(limit).all()
        total = db.query(Order).filter(Order.user_id == user_id).count()
        query_time = time.time() - start_time

        # 记录慢SQL日志（后续会实现）
        print(f"[SLOW SQL] user_id={user_id}, time={query_time:.3f}s")

        return OrderListResponse(total=total, orders=orders)

    # 正常查询
    orders = db.query(Order).filter(Order.user_id == user_id).offset(skip).limit(limit).all()
    total = db.query(Order).filter(Order.user_id == user_id).count()

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
