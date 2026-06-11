# -*- coding: utf-8 -*-
"""活动配置 Schema"""
from pydantic import BaseModel, Field
from typing import Optional


class ActivityConfigResponse(BaseModel):
    """活动配置响应"""
    id: int
    activity_name: str
    max_people: int
    current_people: int
    single_submit_limit: int

    class Config:
        from_attributes = True


class ActivityConfigUpdate(BaseModel):
    """活动配置更新请求"""
    activity_name: Optional[str] = Field(None, max_length=100, description="活动名称")
    max_people: Optional[int] = Field(None, ge=1, description="最大人数上限")
    single_submit_limit: Optional[int] = Field(None, ge=1, le=100, description="单次提交最大人数")
