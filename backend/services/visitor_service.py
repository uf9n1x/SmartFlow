"""游客进出场服务"""
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from sqlalchemy import select
from models.people_log import PeopleLog, OperationType, SourceType
from models.activity_config import ActivityConfig
from core.config import settings


class RateLimitError(Exception):
    """IP 限频异常"""
    pass


class CapacityFullError(Exception):
    """人数已满异常"""
    pass


class InsufficientPeopleError(Exception):
    """当前人数不足异常"""
    pass


async def check_rate_limit(redis: Redis, ip: str) -> bool:
    """检查 IP 限频，返回 True 表示通过，False 表示被限制"""
    key = f"rate_limit:{ip}"
    exists = await redis.exists(key)
    if exists:
        return False
    await redis.setex(key, settings.RATE_LIMIT_SECONDS, 1)
    return True


async def get_current_people(redis: Redis) -> int:
    """从 Redis 获取当前人数"""
    count = await redis.get("activity:current_people")
    return int(count) if count else 0


async def visitor_entry(redis: Redis, db: AsyncSession, count: int, ip: str, user_agent: str):
    """游客进场登记"""
    # 数量校验
    if count < 1 or count > settings.MAX_VISITOR_COUNT:
        raise ValueError(f"单次人数范围为 1~{settings.MAX_VISITOR_COUNT}")

    # IP 限频检查
    if not await check_rate_limit(redis, ip):
        raise RateLimitError("操作过于频繁，请稍后再试")

    # 检查人数上限
    max_people = settings.MAX_PEOPLE  # 默认值
    config = (await db.execute(select(ActivityConfig).limit(1))).scalar_one_or_none()
    if config:
        max_people = config.max_people

    current = await get_current_people(redis)
    if current >= max_people:
        raise CapacityFullError("当前活动区域人数已达到最大上限，请您等待")

    # Redis 原子增加
    new_count = await redis.incrby("activity:current_people", count)
    # 今日进场人数
    await redis.incrby("activity:today_entry", count)

    # 写入日志
    log = PeopleLog(
        operation_type=OperationType.ENTRY,
        source_type=SourceType.VISITOR,
        count=count,
        ip=ip,
        user_agent=user_agent
    )
    db.add(log)
    await db.commit()

    return new_count


async def visitor_exit(redis: Redis, db: AsyncSession, count: int, ip: str, user_agent: str):
    """游客出场登记"""
    if count < 1 or count > settings.MAX_VISITOR_COUNT:
        raise ValueError(f"单次人数范围为 1~{settings.MAX_VISITOR_COUNT}")

    if not await check_rate_limit(redis, ip):
        raise RateLimitError("操作过于频繁，请稍后再试")

    current = await get_current_people(redis)
    if current < count:
        raise InsufficientPeopleError(f"出场人数({count})超过当前在区域人数({current})")

    # Redis 原子减少
    new_count = await redis.decrby("activity:current_people", count)
    if new_count < 0:
        # 如果出现负数（异常情况），重置为0
        await redis.set("activity:current_people", 0)
        new_count = 0
    await redis.incrby("activity:today_exit", count)

    # 写入日志
    log = PeopleLog(
        operation_type=OperationType.EXIT,
        source_type=SourceType.VISITOR,
        count=count,
        ip=ip,
        user_agent=user_agent
    )
    db.add(log)
    await db.commit()

    return new_count
