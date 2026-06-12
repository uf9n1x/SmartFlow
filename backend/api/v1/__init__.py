"""API v1 路由聚合"""
from fastapi import APIRouter
from api.v1.visitor import router as visitor_router
from api.v1.staff import router as staff_router
from api.v1.ws import router as ws_router
from api.v1.auth import router as auth_router
from api.v1.dashboard import router as dashboard_router
from api.v1.logs import router as logs_router
from api.v1.activity import router as activity_router
from api.v1.admin import router as admin_router
from .report import router as report_router

router = APIRouter()
router.include_router(visitor_router)
router.include_router(staff_router)
router.include_router(ws_router)
router.include_router(auth_router)
router.include_router(dashboard_router)
router.include_router(logs_router)
router.include_router(activity_router)
router.include_router(report_router)
router.include_router(admin_router)