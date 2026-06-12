"""管理员 API — 用户管理、系统配置"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.deps import get_current_user, require_admin
from models.people_log import PeopleLog, OperationType, SourceType
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


@router.post("/reset-counter")
async def reset_counter(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """重置当前在场人数为 0（管理员专用）"""
    from core.redis import redis_client
    from api.v1.visitor import get_dashboard_data
    from services.websocket_service import manager

    current = await redis_client.get("activity:current_people")
    current = int(current) if current else 0

    if current <= 0:
        return {"message": "当前人数已为 0，无需重置", "previous_count": 0}

    # 写入系统操作日志（作为 exit，保持基线计算正确）
    log = PeopleLog(
        operation_type=OperationType.EXIT,
        source_type=SourceType.STAFF,
        count=current,
        ip="system",
        user_agent="admin-reset"
    )
    db.add(log)
    await db.commit()

    # Redis 清零
    await redis_client.set("activity:current_people", 0)

    # 广播更新到所有大屏
    dashboard_data = await get_dashboard_data(db)
    dashboard_data["current_people"] = 0
    await manager.broadcast(dashboard_data)

    return {"message": f"已重置，原在场人数: {current}", "previous_count": current}
