"""
活动配置模型模块

定义活动配置表结构，用于存储活动名称、人数上限等配置信息。
"""

from sqlalchemy import Column, Integer, String

from core.base import Base, TimestampMixin


class ActivityConfig(Base, TimestampMixin):
    """活动配置模型"""
    __tablename__ = "activity_config"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="配置ID")
    activity_name = Column(String(100), default="默认活动", comment="活动名称")
    max_people = Column(Integer, default=500, comment="最大人数上限")
    current_people = Column(Integer, default=0, comment="当前人数（快照）")
    single_submit_limit = Column(Integer, default=10, comment="单次提交最大人数")
