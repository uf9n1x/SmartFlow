# -*- coding: utf-8 -*-
"""认证依赖"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from .security import decode_access_token

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """JWT 认证依赖：解析 token 获取当前用户"""
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = payload.get("sub")
        role = payload.get("role")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的认证凭据"
            )
        return {"user_id": int(user_id), "role": role}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证凭据无效或已过期",
        )


async def require_admin(current_user: dict = Depends(get_current_user)):
    """管理员权限依赖"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限"
        )
    return current_user
