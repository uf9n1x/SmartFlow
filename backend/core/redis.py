"""
Redis 连接模块

使用 redis.asyncio 提供单例模式的异步 Redis 连接管理。
"""

import redis.asyncio as aioredis

from .config import settings

# 全局 Redis 连接实例
_redis_client: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    """获取 Redis 异步客户端实例（单例模式），强制 RESP2 协议兼容旧版 Redis"""
    global _redis_client
    if _redis_client is None:
        pool = aioredis.ConnectionPool.from_url(
            settings.REDIS_URL,
            protocol=2,                # 强制 RESP2，兼容 Redis < 6.0
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
        )
        _redis_client = aioredis.Redis(connection_pool=pool)
    return _redis_client


async def disconnect_redis():
    """断开 Redis 连接"""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None
