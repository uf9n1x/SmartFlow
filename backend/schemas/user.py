# -*- coding: utf-8 -*-
"""用户 Schema"""
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    password: str = Field(..., min_length=1, description="密码")


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    role: str


class UserInfo(BaseModel):
    """用户信息"""
    id: int
    username: str
    role: str
    status: str

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """创建用户请求"""
    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    password: str = Field(..., min_length=4, description="密码（最少4位）")
    role: str = Field("staff", description="角色: admin 或 staff")


class UserOut(BaseModel):
    """用户列表响应"""
    id: int
    username: str
    role: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
