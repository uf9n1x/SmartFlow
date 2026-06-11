# -*- coding: utf-8 -*-
"""认证服务"""
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import verify_password, create_access_token
from models.user import User, UserStatus


async def authenticate_user(db: AsyncSession, username: str, password: str):
    """验证用户凭据，返回 JWT token 和用户信息"""
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误"
        )
    if user.status == UserStatus.DISABLED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="账号已禁用"
        )
    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误"
        )

    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "role": user.role.value,
    }
