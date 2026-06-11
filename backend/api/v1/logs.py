"""
日志查询 API 模块

提供操作日志的分页查询接口。
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from schemas.people_log import PeopleLogResponse
from schemas.common import PaginatedResponse
from services.log_service import query_logs

router = APIRouter(prefix="/logs", tags=["日志"])


@router.get("", response_model=PaginatedResponse[PeopleLogResponse])
async def get_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    operation_type: str = Query(None),
    source_type: str = Query(None),
    start_date: str = Query(None),
    end_date: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """分页查询操作日志"""
    result = await query_logs(
        db, page, page_size, operation_type, source_type, start_date, end_date
    )
    return result
