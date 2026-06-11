# -*- coding: utf-8 -*-
"""Schemas 包 - 导出所有 Pydantic Schema"""

# 通用 Schema
from .common import PaginatedResponse, MessageResponse, ErrorResponse

# 用户 Schema
from .user import LoginRequest, LoginResponse, UserInfo

# 活动配置 Schema
from .activity import ActivityConfigResponse, ActivityConfigUpdate

# 人员进出日志 Schema
from .people_log import (
    PeopleCountRequest,
    PeopleCountResponse,
    PeopleLogResponse,
    LogQueryParams,
)

# Dashboard Schema
from .dashboard import DashboardResponse

# 报表 Schema
from .report import ReportQueryParams, ReportDataItem

__all__ = [
    # 通用
    "PaginatedResponse",
    "MessageResponse",
    "ErrorResponse",
    # 用户
    "LoginRequest",
    "LoginResponse",
    "UserInfo",
    # 活动配置
    "ActivityConfigResponse",
    "ActivityConfigUpdate",
    # 人员进出日志
    "PeopleCountRequest",
    "PeopleCountResponse",
    "PeopleLogResponse",
    "LogQueryParams",
    # Dashboard
    "DashboardResponse",
    # 报表
    "ReportQueryParams",
    "ReportDataItem",
]
