# -*- coding: utf-8 -*-
"""通用 Pydantic Schema"""
from pydantic import BaseModel
from typing import Generic, TypeVar, List, Optional

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应"""
    items: List[T]
    total: int
    page: int
    page_size: int


class MessageResponse(BaseModel):
    """消息响应"""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """错误响应"""
    detail: str
