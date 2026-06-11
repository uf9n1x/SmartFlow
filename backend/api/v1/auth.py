# -*- coding: utf-8 -*-
"""认证 API"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from schemas.user import LoginRequest, LoginResponse
from services.auth_service import authenticate_user

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login", response_model=LoginResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    """工作人员登录"""
    result = await authenticate_user(db, req.username, req.password)
    return result
