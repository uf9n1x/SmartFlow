"""
Dashboard API 模块

提供实时 Dashboard 数据查询接口。
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from core.database import get_db
from core.redis import get_redis
from schemas.dashboard import DashboardResponse
from services.dashboard_service import get_dashboard_data

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardResponse)
async def dashboard(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """获取实时 Dashboard 数据"""
    data = await get_dashboard_data(redis, db)
    return data
