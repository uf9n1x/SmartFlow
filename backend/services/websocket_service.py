"""WebSocket 连接管理服务"""
import asyncio
from fastapi import WebSocket
from typing import List
import json


class ConnectionManager:
    """WebSocket 连接管理器（单例模式）"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """接受连接并添加到活动列表"""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """移除断开连接的客户端"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, data: dict):
        """向所有连接的客户端并行广播数据（高并发优化）"""
        if not self.active_connections:
            return

        message = json.dumps(data, ensure_ascii=False)

        async def _send(conn: WebSocket):
            try:
                await conn.send_text(message)
                return None
            except Exception:
                return conn

        results = await asyncio.gather(
            *[_send(c) for c in self.active_connections],
            return_exceptions=True,
        )
        # 清理断开的连接
        dead = [r for r in results if r is not None and not isinstance(r, BaseException)]
        for conn in dead:
            self.active_connections.remove(conn)

    @property
    def connection_count(self) -> int:
        """当前连接数"""
        return len(self.active_connections)


# 全局单例
manager = ConnectionManager()
