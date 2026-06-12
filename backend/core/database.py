"""
数据库连接模块

使用 SQLAlchemy 2.0 异步引擎管理 MySQL 数据库连接，
提供依赖注入用的数据库会话生成器。
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .config import settings

# 创建异步数据库引擎
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_size=30,
    max_overflow=50,
    pool_pre_ping=True,
)

# 创建异步会话工厂
async_session_factory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    """获取数据库会话的异步生成器，用于 FastAPI 依赖注入"""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    """自动创建数据库（如不存在）和所有模型对应的数据库表"""
    from models import Base  # noqa: F401

    # 提取数据库名
    db_name = settings.DATABASE_URL.rsplit("/", 1)[-1].split("?")[0]
    # 连接到 mysql 系统库创建目标数据库
    base_url = settings.DATABASE_URL.rsplit("/", 1)[0] + "/mysql"
    tmp_engine = create_async_engine(base_url, echo=False)
    async with tmp_engine.begin() as conn:
        await conn.execute(text(
            f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        ))
    await tmp_engine.dispose()

    # 在目标数据库中创建表
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def disconnect_database():
    """断开数据库连接，释放连接池资源"""
    await async_engine.dispose()
