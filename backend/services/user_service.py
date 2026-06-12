# -*- coding: utf-8 -*-
"""用户管理服务"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User, UserRole, UserStatus
from core.security import hash_password


async def get_all_users(db: AsyncSession) -> list[User]:
    """获取所有用户列表，按创建时间倒序"""
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return list(result.scalars().all())


async def create_user(db: AsyncSession, username: str, password: str, role: str) -> User:
    """创建新用户，校验用户名唯一，密码自动哈希"""
    # 检查用户名是否已存在
    existing = await db.execute(select(User).where(User.username == username))
    if existing.scalar_one_or_none():
        raise ValueError(f"用户名 '{username}' 已存在")

    # 校验角色合法性
    if role not in (UserRole.ADMIN.value, UserRole.STAFF.value):
        raise ValueError(f"无效的角色: {role}")

    user = User(
        username=username,
        password_hash=hash_password(password),
        role=role,
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def toggle_user_status(db: AsyncSession, user_id: int, current_user_id: int) -> User:
    """切换用户启用/禁用状态，不允许操作自己"""
    if user_id == current_user_id:
        raise ValueError("不能禁用或启用自己的账号")

    user = await db.get(User, user_id)
    if not user:
        raise ValueError("用户不存在")

    user.status = UserStatus.DISABLED if user.status == UserStatus.ACTIVE else UserStatus.ACTIVE
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: int, current_user_id: int) -> bool:
    """删除用户，不允许删除自己"""
    if user_id == current_user_id:
        raise ValueError("不能删除自己的账号")

    user = await db.get(User, user_id)
    if not user:
        raise ValueError("用户不存在")

    await db.delete(user)
    await db.commit()
    return True
