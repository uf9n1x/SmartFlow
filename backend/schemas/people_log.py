# -*- coding: utf-8 -*-
"""人员进出日志 Schema"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from models.people_log import OperationType, SourceType


class PeopleCountRequest(BaseModel):
    """进出场人数请求"""
    count: int = Field(..., ge=1, description="人数")


class PeopleCountResponse(BaseModel):
    """进出场人数响应"""
    message: str
    current_people: int
    operation_type: str
    count: int


class PeopleLogResponse(BaseModel):
    """日志记录响应"""
    id: int
    operation_type: str
    source_type: str
    operator_id: Optional[int] = None
    count: int
    ip: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class LogQueryParams(BaseModel):
    """日志查询参数"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")
    operation_type: Optional[str] = Field(None, description="操作类型: entry/exit")
    source_type: Optional[str] = Field(None, description="来源类型: visitor/staff")
    start_date: Optional[str] = Field(None, description="开始日期 YYYY-MM-DD")
    end_date: Optional[str] = Field(None, description="结束日期 YYYY-MM-DD")
