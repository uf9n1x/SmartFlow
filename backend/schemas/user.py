# -*- coding: utf-8 -*-
"""用户 Schema"""
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
