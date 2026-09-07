"""
API Package
API路由包
"""
from fastapi import APIRouter
from app.api.users import router as users_router
from app.api.orders import router as orders_router
from app.api.logs import router as logs_router
from app.api.metrics import router as metrics_router
from app.api.alerts import router as alerts_router
from app.api.llm import router as llm_router

api_router = APIRouter()

# 注册路由
api_router.include_router(users_router)
api_router.include_router(orders_router)
api_router.include_router(logs_router)
api_router.include_router(metrics_router)
api_router.include_router(alerts_router)
api_router.include_router(llm_router)

__all__ = ['api_router']
