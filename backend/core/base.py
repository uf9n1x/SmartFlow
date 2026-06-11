"""
SQLAlchemy 声明式基类模块

提供 Base 声明式基类和通用时间戳混入类。
"""

from sqlalchemy import Column, DateTime, func
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """SQLAlchemy 声明式基类"""
    pass


class TimestampMixin:
    """时间戳混入类：自动记录创建和更新时间"""
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )
