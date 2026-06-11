"""
日志查询服务模块

提供操作日志的分页查询和条件筛选业务逻辑。
"""

from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from models.people_log import PeopleLog


async def query_logs(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    operation_type: Optional[str] = None,
    source_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    """分页查询操作日志

    支持按操作类型、来源类型、日期范围筛选，按创建时间倒序排列。
    """
    query = select(PeopleLog)
    count_query = select(func.count(PeopleLog.id))

    # 按操作类型筛选
    if operation_type:
        query = query.where(PeopleLog.operation_type == operation_type)
        count_query = count_query.where(PeopleLog.operation_type == operation_type)

    # 按来源类型筛选
    if source_type:
        query = query.where(PeopleLog.source_type == source_type)
        count_query = count_query.where(PeopleLog.source_type == source_type)

    # 按开始日期筛选
    if start_date:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        query = query.where(PeopleLog.created_at >= start)
        count_query = count_query.where(PeopleLog.created_at >= start)

    # 按结束日期筛选（包含当天全天）
    if end_date:
        end = datetime.strptime(end_date, "%Y-%m-%d")
        query = query.where(PeopleLog.created_at < end.replace(hour=23, minute=59, second=59))
        count_query = count_query.where(PeopleLog.created_at < end.replace(hour=23, minute=59, second=59))

    # 查询总记录数
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # 分页查询，按创建时间倒序
    query = query.order_by(PeopleLog.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }
