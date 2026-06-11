"""
应用配置模块

使用 pydantic-settings 读取 .env 文件和环境变量配置。
优先级：.env 文件 > 系统环境变量 > 代码默认值
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# 自动定位项目根目录的 .env 文件
# 无论从哪个目录启动 uvicorn，都从 backend/core/config.py 向上两级找到项目根目录
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """应用全局配置
    支持两种配置方式（.env 文件优先级更高）：
    1. 在项目根目录创建 .env 文件，写入键值对
    2. 设置系统环境变量（export / set）
    """

    # 数据库配置
    DATABASE_URL: str = "mysql+aiomysql://root:password@localhost:3306/people_counting"

    # Redis 配置
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT 安全配置
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8小时

    # 频率限制配置
    RATE_LIMIT_SECONDS: int = 10

    # 人数上限配置
    MAX_PEOPLE: int = 500

    # 访客和员工最大数量配置
    MAX_VISITOR_COUNT: int = 10
    MAX_STAFF_COUNT: int = 50

    # 默认管理员账号（仅首次启动自动创建时使用）
    DEFAULT_ADMIN_USERNAME: str = "admin"
    DEFAULT_ADMIN_PASSWORD: str = "admin123"

    model_config = SettingsConfigDict(
        env_file=str(_PROJECT_ROOT / ".env"),   # 固定指向项目根目录的 .env
        env_file_encoding="utf-8",
        extra="ignore",                          # 忽略 .env 中未定义的键
    )


# 全局单例配置对象
settings = Settings()
