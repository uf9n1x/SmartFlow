"""活动配置服务"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.activity_config import ActivityConfig
from fastapi import HTTPException, status


async def get_activity_config(db: AsyncSession):
    """获取活动配置"""
    result = await db.execute(select(ActivityConfig).limit(1))
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="活动配置不存在"
        )
    return config


async def update_activity_config(db: AsyncSession, data: dict):
    """更新活动配置"""
    result = await db.execute(select(ActivityConfig).limit(1))
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="活动配置不存在"
        )

    # 只更新传入的字段
    for field, value in data.items():
        if value is not None:
            setattr(config, field, value)

    await db.commit()
    await db.refresh(config)
    return config
