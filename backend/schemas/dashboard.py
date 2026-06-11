# -*- coding: utf-8 -*-
"""Dashboard Schema"""
from pydantic import BaseModel


class DashboardResponse(BaseModel):
    """Dashboard 数据响应"""
    current_people: int
    max_people: int
    remaining_capacity: int
    usage_rate: float
    today_entry: int
    today_exit: int
    total_entry: int
    total_exit: int
    is_full: bool
