"""
数据库初始化脚本

在应用启动时自动创建数据库表，并初始化默认管理员账号和默认活动配置。
管理员账号凭据通过环境变量 DEFAULT_ADMIN_USERNAME / DEFAULT_ADMIN_PASSWORD 配置。
"""

from sqlalchemy import select

from .database import async_session_factory, create_tables
from .security import hash_password
from .config import settings
from models.user import User, UserRole, UserStatus
from models.activity_config import ActivityConfig


async def init_database():
    """初始化数据库表并创建默认数据（管理员账号及活动配置）"""
    await create_tables()

    async with async_session_factory() as session:
        # 检查是否已有管理员账号，如无则创建默认管理员
        result = await session.execute(select(User).where(User.username == settings.DEFAULT_ADMIN_USERNAME))
        if not result.scalar_one_or_none():
            admin = User(
                username=settings.DEFAULT_ADMIN_USERNAME,
                password_hash=hash_password(settings.DEFAULT_ADMIN_PASSWORD),
                role=UserRole.ADMIN,
                status=UserStatus.ACTIVE,
            )
            session.add(admin)

        # 检查是否已有活动配置，如无则创建默认配置
        result = await session.execute(select(ActivityConfig).limit(1))
        if not result.scalar_one_or_none():
            config = ActivityConfig(
                activity_name="默认活动",
                max_people=500,
                current_people=0,
                single_submit_limit=10,
            )
            session.add(config)

        await session.commit()
