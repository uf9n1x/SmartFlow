# -*- coding: utf-8 -*-
"""报表 Schema"""
from pydantic import BaseModel, Field
from typing import Optional, Literal


class ReportQueryParams(BaseModel):
    """报表查询参数"""
    start_date: Optional[str] = Field(None, description="开始日期 YYYY-MM-DD")
    end_date: Optional[str] = Field(None, description="结束日期 YYYY-MM-DD")
    granularity: Literal["day", "week", "month"] = Field("day", description="统计粒度")
    format: Literal["xlsx", "csv"] = Field("xlsx", description="导出格式")


class ReportDataItem(BaseModel):
    """报表数据项"""
    period: str
    entry_count: int
    exit_count: int
    net_count: int
