"""
Dashboard 服务模块

提供 Dashboard 实时数据汇总的业务逻辑。
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from redis.asyncio import Redis

from models.people_log import PeopleLog, OperationType
from models.activity_config import ActivityConfig


async def get_dashboard_data(redis: Redis, db: AsyncSession):
    """获取 Dashboard 汇总数据

    从 Redis 获取实时在场人数和今日进出场统计，
    从数据库获取配置信息和历史累计数据。
    """
    # 从 Redis 获取实时数据
    current_people = int(await redis.get("activity:current_people") or 0)
    today_entry = int(await redis.get("activity:today_entry") or 0)
    today_exit = int(await redis.get("activity:today_exit") or 0)

    # 从数据库获取配置
    config = (await db.execute(select(ActivityConfig).limit(1))).scalar_one_or_none()
    max_people = config.max_people if config else 500
    remaining = max(0, max_people - current_people)
    usage_rate = round(current_people / max_people * 100, 2) if max_people > 0 else 0
    is_full = current_people >= max_people

    # 从数据库统计总进出场人数
    total_entry_result = await db.execute(
        select(func.sum(case((PeopleLog.operation_type == "entry", PeopleLog.count), else_=0)))
        .where(PeopleLog.operation_type == OperationType.ENTRY)
    )
    total_entry = int(total_entry_result.scalar() or 0)

    total_exit_result = await db.execute(
        select(func.sum(case((PeopleLog.operation_type == "exit", PeopleLog.count), else_=0)))
        .where(PeopleLog.operation_type == OperationType.EXIT)
    )
    total_exit = int(total_exit_result.scalar() or 0)

    return {
        "current_people": current_people,
        "max_people": max_people,
        "remaining_capacity": remaining,
        "usage_rate": usage_rate,
        "today_entry": today_entry,
        "today_exit": today_exit,
        "total_entry": total_entry,
        "total_exit": total_exit,
        "is_full": is_full,
    }
