"""WebSocket API"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.websocket_service import manager
from services.dashboard_service import get_dashboard_data
from core.redis import get_redis
from core.database import async_session_factory

router = APIRouter()


@router.websocket("/ws/dashboard")
async def dashboard_websocket(websocket: WebSocket):
    """Dashboard 实时数据推送 WebSocket"""
    await manager.connect(websocket)
    try:
        # 连接后立即推送一次数据
        redis = await get_redis()
        async with async_session_factory() as db:
            data = await get_dashboard_data(redis, db)
            data["connection_count"] = manager.connection_count
            await websocket.send_json(data)

        # 保持连接，接收心跳
        while True:
            try:
                msg = await websocket.receive_text()
                if msg == "ping":
                    await websocket.send_text("pong")
            except WebSocketDisconnect:
                break
    except Exception as e:
        try:
            await websocket.send_json({"error": str(e)})
        except Exception:
            pass
    finally:
        manager.disconnect(websocket)
