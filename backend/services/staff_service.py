# -*- coding: utf-8 -*-
"""工作人员进出场服务"""
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from models.people_log import PeopleLog, OperationType, SourceType


async def staff_entry(redis: Redis, db: AsyncSession, count: int, operator_id: int):
    """工作人员进场登记"""
    if count < 1 or count > settings.MAX_STAFF_COUNT:
        raise ValueError(f"单次人数范围为 1~{settings.MAX_STAFF_COUNT}")

    # Redis 原子增加
    new_count = await redis.incrby("activity:current_people", count)
    await redis.incrby("activity:today_entry", count)

    # 写入日志
    log = PeopleLog(
        operation_type=OperationType.ENTRY,
        source_type=SourceType.STAFF,
        operator_id=operator_id,
        count=count,
        ip="staff",
        user_agent="staff-client",
    )
    db.add(log)
    await db.commit()

    return new_count


async def staff_exit(redis: Redis, db: AsyncSession, count: int, operator_id: int):
    """工作人员出场登记"""
    if count < 1 or count > settings.MAX_STAFF_COUNT:
        raise ValueError(f"单次人数范围为 1~{settings.MAX_STAFF_COUNT}")

    current = await redis.get("activity:current_people")
    current = int(current) if current else 0
    if current < count:
        raise ValueError(f"出场人数({count})超过当前在区域人数({current})")

    new_count = await redis.decrby("activity:current_people", count)
    if new_count < 0:
        await redis.set("activity:current_people", 0)
        new_count = 0
    await redis.incrby("activity:today_exit", count)

    log = PeopleLog(
        operation_type=OperationType.EXIT,
        source_type=SourceType.STAFF,
        operator_id=operator_id,
        count=count,
        ip="staff",
        user_agent="staff-client",
    )
    db.add(log)
    await db.commit()

    return new_count
