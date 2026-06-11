"""WebSocket 连接管理服务"""
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
        """向所有连接的客户端广播数据"""
        dead_connections = []
        message = json.dumps(data, ensure_ascii=False)
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                dead_connections.append(connection)
        # 清理断开的连接
        for conn in dead_connections:
            self.active_connections.remove(conn)

    @property
    def connection_count(self) -> int:
        """当前连接数"""
        return len(self.active_connections)


# 全局单例
manager = ConnectionManager()
