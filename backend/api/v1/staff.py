# -*- coding: utf-8 -*-
"""工作人员进出场 API"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.deps import get_current_user
from core.redis import get_redis
from schemas.people_log import PeopleCountRequest, PeopleCountResponse
from services.staff_service import staff_entry, staff_exit
from services.websocket_service import manager
from services.dashboard_service import get_dashboard_data

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/staff", tags=["工作人员"])


@router.post("/entry", response_model=PeopleCountResponse)
async def staff_entry_api(
    req: PeopleCountRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    current_user: dict = Depends(get_current_user),
):
    """工作人员进场登记（需JWT认证）"""
    try:
        new_count = await staff_entry(redis, db, req.count, current_user["user_id"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 广播失败不影响主流程
    try:
        broadcast_data = await get_dashboard_data(redis, db)
        broadcast_data["connection_count"] = manager.connection_count
        await manager.broadcast(broadcast_data)
    except Exception as e:
        logger.warning(f"广播 Dashboard 数据失败: {e}")

    return PeopleCountResponse(
        message=f"进场{req.count}人登记成功",
        current_people=new_count,
        operation_type="entry",
        count=req.count,
    )


@router.post("/exit", response_model=PeopleCountResponse)
async def staff_exit_api(
    req: PeopleCountRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    current_user: dict = Depends(get_current_user),
):
    """工作人员出场登记（需JWT认证）"""
    try:
        new_count = await staff_exit(redis, db, req.count, current_user["user_id"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 广播失败不影响主流程
    try:
        broadcast_data = await get_dashboard_data(redis, db)
        broadcast_data["connection_count"] = manager.connection_count
        await manager.broadcast(broadcast_data)
    except Exception as e:
        logger.warning(f"广播 Dashboard 数据失败: {e}")

    return PeopleCountResponse(
        message=f"出场{req.count}人登记成功",
        current_people=new_count,
        operation_type="exit",
        count=req.count,
    )
