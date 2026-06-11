"""
用户模型模块

定义用户表结构和相关枚举类型。
"""

import enum

from sqlalchemy import Column, Enum as SQLEnum, Integer, String

from core.base import Base, TimestampMixin


class UserRole(str, enum.Enum):
    """用户角色枚举"""
    ADMIN = "admin"
    STAFF = "staff"


class UserStatus(str, enum.Enum):
    """用户状态枚举"""
    ACTIVE = "active"
    DISABLED = "disabled"


class User(Base, TimestampMixin):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="用户ID")
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    role = Column(SQLEnum(UserRole), default=UserRole.STAFF, nullable=False, comment="角色")
    status = Column(SQLEnum(UserStatus), default=UserStatus.ACTIVE, nullable=False, comment="状态")
