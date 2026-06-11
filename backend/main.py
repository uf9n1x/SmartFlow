"""
FastAPI 应用入口

创建 FastAPI 应用实例，配置 CORS 中间件、生命周期事件和路由注册。
"""

import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1 import router as v1_router
from core.database import disconnect_database
from core.init_db import init_database
from core.redis import disconnect_redis, get_redis

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理：启动时初始化数据库和 Redis，关闭时释放资源"""
    try:
        logger.info("正在连接 Redis...")
        await get_redis()
        logger.info("Redis 连接成功")
    except Exception as e:
        logger.error(f"Redis 连接失败: {e}")
        raise

    try:
        logger.info("正在初始化数据库...")
        await init_database()
        logger.info("数据库初始化成功")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise

    logger.info("应用启动完成")
    yield
    logger.info("正在关闭连接...")
    await disconnect_database()
    await disconnect_redis()
    logger.info("应用已关闭")


# 创建 FastAPI 应用实例
app = FastAPI(
    title="SmartFlow 智流云",
    description="SmartFlow 智流云 - 大型活动实时客流统计与管控平台 API",
    version="0.1.0",
    docs_url=None,      # 关闭 Swagger UI
    redoc_url=None,     # 关闭 ReDoc
    lifespan=lifespan,
)

# 配置 CORS 中间件（开发模式允许所有来源）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 API v1 路由
app.include_router(v1_router, prefix="/api/v1")


@app.get("/")
async def root_health_check():
    """根路径健康检查接口"""
    return {"status": "ok", "message": "SmartFlow 智流云 运行中"}
