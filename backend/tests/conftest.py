# -*- coding: utf-8 -*-
"""测试配置和共享 fixtures

提供 Mock Redis、Mock 数据库会话和测试客户端的 fixtures，
并处理 FastAPI 生命周期中的数据库/Redis 连接模拟。
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient


# ==================== Mock Redis ====================

@pytest.fixture
def mock_redis():
    """创建 Mock Redis 异步客户端

    默认行为：
    - get 返回 b"0"（当前人数为0）
    - exists 返回 False（无不存在的键，无频率限制）
    - incrby 返回 10（增量后默认返回值）
    - decrby 返回 5（减量后默认返回值）
    """
    redis = AsyncMock()
    redis.get = AsyncMock(return_value=b"0")
    redis.set = AsyncMock()
    redis.setex = AsyncMock()
    redis.exists = AsyncMock(return_value=False)
    redis.incrby = AsyncMock(return_value=10)
    redis.decrby = AsyncMock(return_value=5)
    redis.keys = AsyncMock(return_value=[])
    return redis


# ==================== Mock 数据库会话 ====================

@pytest.fixture
def mock_db():
    """创建 Mock 异步数据库会话

    提供 execute / add / commit / refresh 等方法的基础 mock。
    """
    session = AsyncMock()
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.scalars = MagicMock()
    return session


# ==================== Mock FastAPI 生命周期 ====================

def _patch_lifespan(mock_redis):
    """返回 lifespan 中需要 patch 的目标和替换值列表

    防止 TestClient 启动时尝试连接真实的 Redis 和数据库。
    """
    return [
        patch('core.redis.get_redis', new=AsyncMock(return_value=mock_redis)),
        patch('core.redis.disconnect_redis', new=AsyncMock()),
        patch('core.database.disconnect_database', new=AsyncMock()),
        patch('core.init_db.init_database', new=AsyncMock()),
    ]


# ==================== TestClient 共享 fixture ====================

@pytest.fixture
def client(mock_redis, mock_db):
    """创建 FastAPI 测试客户端

    自动覆盖数据库和 Redis 依赖，并注册 visitor 路由
    （解决 router.py 中未注册 visitor 路由的问题）。
    """
    from main import app
    from core.database import get_db
    from core.redis import get_redis
    from api.v1.visitor import router as visitor_router

    # 确保 visitor 路由已注册（router.py 中可能遗漏）
    existing_paths = [route.path for route in app.routes]
    if not any("visitor" in p for p in existing_paths):
        app.include_router(visitor_router, prefix="/api/v1")

    async def override_get_db():
        yield mock_db

    async def override_get_redis():
        return mock_redis

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis

    # 模拟生命周期中的真实连接
    patches = _patch_lifespan(mock_redis)
    for p in patches:
        p.start()

    with TestClient(app) as c:
        yield c

    for p in patches:
        p.stop()
    app.dependency_overrides.clear()


# ==================== pytest 配置 ====================

# 为 asyncio 测试设置默认事件循环作用域
# pytest-asyncio 自动处理异步测试
