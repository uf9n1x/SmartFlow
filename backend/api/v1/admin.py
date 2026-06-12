"""管理员 API — 用户管理、系统配置"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.deps import get_current_user, require_admin
from schemas.user import UserCreate, UserOut
from services import user_service as user_svc

router = APIRouter(prefix="/admin", tags=["管理员"])


@router.get("/users", response_model=list[UserOut])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """获取所有用户列表（仅管理员）"""
    users = await user_svc.get_all_users(db)
    return users


@router.post("/users", response_model=UserOut)
async def add_user(
    req: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """创建新用户（仅管理员）"""
    try:
        user = await user_svc.create_user(db, req.username, req.password, req.role)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/users/{user_id}/toggle")
async def toggle_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """启用/禁用用户（仅管理员，不能操作自己）"""
    try:
        user = await user_svc.toggle_user_status(db, user_id, current_user["user_id"])
        return {"message": "操作成功", "status": user.status.value}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/users/{user_id}")
async def remove_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """删除用户（仅管理员，不能删除自己）"""
    try:
        await user_svc.delete_user(db, user_id, current_user["user_id"])
        return {"message": "删除成功"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
