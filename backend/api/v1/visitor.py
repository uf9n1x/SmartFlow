"""游客进出场 API"""
import logging
from fastapi import APIRouter, Depends, Request

logger = logging.getLogger(__name__)

from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from core.database import get_db
from core.redis import get_redis
from schemas.people_log import PeopleCountRequest, PeopleCountResponse
from services.visitor_service import visitor_entry, visitor_exit, RateLimitError, CapacityFullError, InsufficientPeopleError
from services.websocket_service import manager
from services.dashboard_service import get_dashboard_data
from fastapi import HTTPException

router = APIRouter(prefix="/visitor", tags=["游客"])

@router.post("/entry", response_model=PeopleCountResponse)
async def entry(
    req: PeopleCountRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    """游客进场登记"""
    ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "")
    try:
        new_count = await visitor_entry(redis, db, req.count, ip, user_agent)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except CapacityFullError as e:
        raise HTTPException(status_code=403, detail=str(e))

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
        count=req.count
    )

@router.post("/exit", response_model=PeopleCountResponse)
async def exit_people(
    req: PeopleCountRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    """游客出场登记"""
    ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "")
    try:
        new_count = await visitor_exit(redis, db, req.count, ip, user_agent)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except InsufficientPeopleError as e:
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
        count=req.count
    )
