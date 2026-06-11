"""活动配置 API"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.deps import require_admin
from schemas.activity import ActivityConfigResponse, ActivityConfigUpdate
from services.activity_service import get_activity_config, update_activity_config

router = APIRouter(prefix="/activity", tags=["活动配置"])


@router.get("/config", response_model=ActivityConfigResponse)
async def get_config(db: AsyncSession = Depends(get_db)):
    """获取活动配置（所有人可查看）"""
    config = await get_activity_config(db)
    return config


@router.put("/config", response_model=ActivityConfigResponse)
async def update_config(
    data: ActivityConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """更新活动配置（仅管理员）"""
    update_data = data.model_dump(exclude_unset=True)
    config = await update_activity_config(db, update_data)
    return config
