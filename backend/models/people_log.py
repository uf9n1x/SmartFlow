"""
人员进出日志模型模块

定义人员进出操作日志表结构和相关枚举类型。
"""

import enum

from sqlalchemy import Column, DateTime, Enum as SQLEnum, Integer, String, func

from core.base import Base


class OperationType(str, enum.Enum):
    """操作类型枚举：进场/离场"""
    ENTRY = "entry"
    EXIT = "exit"


class SourceType(str, enum.Enum):
    """人员来源类型枚举"""
    VISITOR = "visitor"
    STAFF = "staff"


class PeopleLog(Base):
    """人员进出日志模型"""
    __tablename__ = "people_logs"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="日志ID")
    operation_type = Column(SQLEnum(OperationType), nullable=False, comment="操作类型：entry/exit")
    source_type = Column(SQLEnum(SourceType), nullable=False, comment="来源：visitor/staff")
    operator_id = Column(Integer, nullable=True, comment="操作员ID（工作人员为空）")
    count = Column(Integer, nullable=False, comment="人数")
    ip = Column(String(45), nullable=True, comment="客户端IP")
    user_agent = Column(String(500), nullable=True, comment="User-Agent")
    created_at = Column(DateTime, server_default=func.now(), index=True, comment="操作时间")
