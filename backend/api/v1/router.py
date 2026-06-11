"""
API v1 路由聚合模块

将各业务模块的路由统一注册到 v1 前缀下。
"""

from fastapi import APIRouter

from .auth import router as auth_router
from .dashboard import router as dashboard_router
from .logs import router as logs_router
from .report import router as report_router
from .staff import router as staff_router

router = APIRouter()

# 注册各业务模块子路由（各子路由已自带 prefix 和 tags）
router.include_router(auth_router)
router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
router.include_router(logs_router, prefix="/logs", tags=["日志"])
router.include_router(report_router)
router.include_router(staff_router)


@router.get("/health")
async def v1_health_check():
    """API v1 健康检查接口"""
    return {"status": "ok", "version": "v1"}
